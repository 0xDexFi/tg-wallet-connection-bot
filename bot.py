"""
Solana Wallet Connection Tracker - Telegram Bot
Advanced on-chain analysis using ZachXBT/Chainalysis techniques.
"""

import re
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import TELEGRAM_BOT_TOKEN
from wallet_analyzer import analyze_wallet, format_analysis_result

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Solana address regex (base58, 32-44 chars)
SOLANA_ADDRESS_REGEX = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")


def is_valid_solana_address(address: str) -> bool:
    """Validate Solana address format."""
    return bool(SOLANA_ADDRESS_REGEX.match(address))


def truncate_address(address: str, chars: int = 4) -> str:
    """Truncate address for display."""
    return f"{address[:chars]}...{address[-chars:]}"


def format_signals(signals: list[str]) -> str:
    """Format signal tags for display."""
    signal_emojis = {
        "FUNDER": "💰",
        "SAME_FUNDER": "👥",
        "SAME_FUNDER_VIA": "👥",
        "FEE_PAYER": "⛽",
        "BIDIRECTIONAL": "↔️",
        "HIGH_FREQ": "🔥",
        "MED_FREQ": "📊",
        "ROUND_AMT": "🎯",
        "LARGE_XFER": "💎",
        "TIMING": "⏰",
        "COMMON_CP_HIGH": "🔗",
        "COMMON_CP": "🔗",
    }
    return " ".join(signal_emojis.get(s, f"[{s}]") for s in signals)


def format_results(results: dict) -> str:
    """Format analysis results for Telegram message."""
    if "error" in results:
        return f"❌ Error: {results['error']}"

    lines = [
        "🔍 **WALLET ANALYSIS REPORT**",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📍 Target: `{results['address']}`",
        f"📊 Transactions analyzed: {results['transaction_count']}",
        "",
    ]

    # Funder information (highest priority)
    if results.get("funder"):
        lines.append("💰 **FUNDING CHAIN:**")
        lines.append(f"   └─ Funder: `{results['funder']}`")
        if results.get("funder_of_funder"):
            lines.append(f"      └─ Funder's Funder: `{truncate_address(results['funder_of_funder'], 6)}`")
        lines.append("")

    # Same funder cluster (very high signal)
    if results.get("same_funder_cluster"):
        lines.append("👥 **SAME FUNDER CLUSTER** (likely same owner):")
        for addr in results["same_funder_cluster"][:5]:
            lines.append(f"   • `{addr}`")
        if len(results["same_funder_cluster"]) > 5:
            lines.append(f"   ... and {len(results['same_funder_cluster']) - 5} more")
        lines.append("")

    # Direct connections (Hop 1)
    direct = results.get("direct_connections", [])
    if direct:
        lines.append("🎯 **DIRECT CONNECTIONS (Hop 1):**")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        for i, conn in enumerate(direct[:12], 1):
            score = conn["score"]
            signals = format_signals(conn.get("signals", []))

            # Score indicator
            if score >= 100:
                score_icon = "🔴"  # Critical connection
            elif score >= 50:
                score_icon = "🟠"  # Strong connection
            elif score >= 25:
                score_icon = "🟡"  # Medium connection
            else:
                score_icon = "⚪"  # Weak connection

            lines.append(f"{score_icon} **#{i}** Score: {score}")
            lines.append(f"   `{conn['address']}`")

            if signals:
                lines.append(f"   {signals}")

            # Transaction details
            details = []
            if conn.get("sent_sol", 0) > 0:
                details.append(f"sent {conn['sent_sol']} SOL")
            if conn.get("received_sol", 0) > 0:
                details.append(f"recv {conn['received_sol']} SOL")
            if conn.get("sent_usd", 0) > 0:
                details.append(f"sent ${conn['sent_usd']}")
            if conn.get("received_usd", 0) > 0:
                details.append(f"recv ${conn['received_usd']}")
            if details:
                lines.append(f"   💵 {', '.join(details)}")
            # Show total value
            total_val = conn.get("total_value_usd", 0)
            if total_val > 0:
                lines.append(f"   💰 Total: ~${total_val:,.0f}")

            lines.append("")

    else:
        lines.append("No direct connections found.")
        lines.append("")

    # Bidirectional cluster
    if results.get("bidirectional_cluster"):
        lines.append("↔️ **BIDIRECTIONAL TRANSFERS** (strong signal):")
        for addr in results["bidirectional_cluster"][:5]:
            lines.append(f"   • `{truncate_address(addr, 6)}`")
        lines.append("")

    # Hop 2 connections
    hop2 = results.get("hop2_connections", [])
    if hop2:
        lines.append("🔗 **SECONDARY CONNECTIONS (Hop 2):**")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        for i, conn in enumerate(hop2[:8], 1):
            score = conn["score"]
            via = conn.get("connected_via", [])
            common_cp = conn.get("common_counterparties", 0)

            lines.append(f"**#{i}** Score: {round(score, 1)}")
            lines.append(f"   `{conn['address']}`")

            if via:
                via_str = ", ".join(truncate_address(v, 4) for v in via[:2])
                lines.append(f"   via: {via_str}")

            if common_cp > 0:
                lines.append(f"   🔗 {common_cp} common counterparties")

            lines.append("")

    # Legend
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("📖 **SIGNAL LEGEND:**")
    lines.append("💰 Funder | 👥 Same Funder | ⛽ Fee Payer")
    lines.append("↔️ Bidirectional | 🔥 High Freq | 🎯 Round Amt")
    lines.append("💎 Large Transfer | ⏰ Timing Match | 🔗 Common CP")

    return "\n".join(lines)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_text = """
🔍 **Solana Wallet Connection Tracker**

Advanced on-chain analysis to find wallets potentially belonging to the same person.

**How it works:**
• Traces funding chains (who funded who)
• Detects same-funder clusters
• Analyzes bidirectional transfers
• Checks timing correlations
• Finds common counterparties
• 2-hop deep analysis

**Commands:**
• `/check <address>` - Analyze a wallet
• `/help` - Show detailed help

**Analysis Signals:**
🔴 Score ≥100 (Critical - likely same owner)
🟠 Score ≥50 (Strong connection)
🟡 Score ≥25 (Medium connection)
⚪ Score <25 (Weak connection)

Send `/check` followed by any Solana wallet address to start!
    """
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = """
🔍 **WALLET ANALYZER HELP**

**Usage:**
`/check <wallet_address>`

**Example:**
`/check 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU`

**What the bot analyzes:**

💰 **Funder Detection**
Finds who first funded the wallet - strongest ownership signal.

👥 **Same Funder Clustering**
Wallets funded by the same source are likely the same owner.

⛽ **Fee Payer Analysis**
Tracks who pays transaction fees - Solana-specific signal.

↔️ **Bidirectional Transfers**
Two-way transfers indicate close relationship.

⏰ **Timing Correlation**
Wallets active at the same hours suggest same owner.

🔗 **Common Counterparties**
Shared transaction partners indicate connection.

🎯 **Amount Patterns**
Round number transfers suggest intentional movement.

**Scoring System:**
• FUNDER: +100
• SAME_FUNDER: +90
• FEE_PAYER: +60
• BIDIRECTIONAL: +50
• COMMON_CP: +25-40
• TIMING: +30
• HIGH_FREQ: +25
• ROUND_AMT: +20

**Filtered Out:**
CEXs, DEXs, LPs, protocols, system programs, bridges, NFT marketplaces
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /check command."""
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a wallet address.\n"
            "Usage: `/check <wallet_address>`",
            parse_mode="Markdown",
        )
        return

    address = context.args[0].strip()

    if not is_valid_solana_address(address):
        await update.message.reply_text(
            "❌ Invalid Solana address format.\n"
            "Please provide a valid base58 address (32-44 characters)."
        )
        return

    # Send initial message
    status_msg = await update.message.reply_text(
        f"🔍 Analyzing wallet...\n"
        f"`{truncate_address(address, 8)}`\n\n"
        f"⏳ Fetching transactions...",
        parse_mode="Markdown",
    )

    try:
        # Update status
        await status_msg.edit_text(
            f"🔍 Analyzing wallet...\n"
            f"`{truncate_address(address, 8)}`\n\n"
            f"⏳ Processing hop-1 connections...",
            parse_mode="Markdown",
        )

        # Run analysis
        result = await analyze_wallet(address)
        formatted_result = format_analysis_result(result)
        formatted_text = format_results(formatted_result)

        # Split message if too long (Telegram limit is 4096 chars)
        if len(formatted_text) > 4000:
            parts = []
            current_part = ""
            for line in formatted_text.split("\n"):
                if len(current_part) + len(line) + 1 > 4000:
                    parts.append(current_part)
                    current_part = line
                else:
                    current_part += "\n" + line if current_part else line
            if current_part:
                parts.append(current_part)

            await status_msg.edit_text(parts[0], parse_mode="Markdown")
            for part in parts[1:]:
                await update.message.reply_text(part, parse_mode="Markdown")
        else:
            await status_msg.edit_text(formatted_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error analyzing wallet {address}: {e}")
        await status_msg.edit_text(
            f"❌ An error occurred while analyzing the wallet:\n`{str(e)}`",
            parse_mode="Markdown",
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Run the bot."""
    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("check", check_command))

    # Add error handler
    app.add_error_handler(error_handler)

    # Start polling
    logger.info("Starting Solana Wallet Connection Tracker bot...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
