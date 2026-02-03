"""Telegram bot for Solana wallet connection tracking."""

import re
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import TELEGRAM_BOT_TOKEN
from wallet_analyzer import analyze_wallet

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


def format_address(address: str, length: int = 8) -> str:
    """Shorten address for display."""
    if len(address) <= length * 2:
        return address
    return f"{address[:length]}...{address[-length:]}"


def format_results(results: dict) -> str:
    """Format analysis results for Telegram message."""
    if "error" in results:
        return f"Error: {results['error']}"

    lines = [
        f"Wallet Analysis",
        f"Target: `{results['address']}`",
        f"Transactions analyzed: {results['transaction_count']}",
        "",
    ]

    # Funder section
    if results.get("funder"):
        lines.append(f"**Initial Funder:**")
        lines.append(f"`{results['funder']}`")
        lines.append("")

    # Direct connections
    direct = results.get("direct_connections", [])
    if direct:
        lines.append(f"**Direct Connections (Hop 1):**")
        for i, conn in enumerate(direct[:10], 1):
            addr = format_address(conn["address"])
            score = conn["score"]
            funder_tag = " [FUNDER]" if conn.get("is_funder") else ""
            sent = conn["sent_sol"]
            received = conn["received_sol"]

            lines.append(f"{i}. `{conn['address']}`")
            lines.append(f"   Score: {score:.1f}{funder_tag}")
            if sent > 0 or received > 0:
                lines.append(f"   SOL: sent {sent}, received {received}")
            lines.append("")
    else:
        lines.append("No direct connections found.")
        lines.append("")

    # Hop 2 connections
    hop2 = results.get("hop2_connections", [])
    if hop2:
        lines.append(f"**Secondary Connections (Hop 2):**")
        for i, conn in enumerate(hop2[:5], 1):
            lines.append(f"{i}. `{conn['address']}`")
            lines.append(f"   Score: {conn['score']}")
            via_wallets = [v["wallet"][:8] + "..." for v in conn["connected_via"][:2]]
            lines.append(f"   Via: {', '.join(via_wallets)}")
            lines.append("")

    return "\n".join(lines)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_text = """
Welcome to the Solana Wallet Connection Tracker!

This bot helps you find potentially connected wallets belonging to the same person by analyzing transaction patterns.

**Commands:**
/check <address> - Analyze a wallet address
/help - Show this help message

**How it works:**
1. Fetches transaction history for the target wallet
2. Identifies all interacted addresses
3. Analyzes secondary connections (2 hops deep)
4. Filters out exchanges, DEXs, and protocols
5. Scores connections by likelihood

Send /check followed by a Solana wallet address to get started!
    """
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = """
**Solana Wallet Connection Tracker**

**Usage:**
/check <wallet_address>

**Example:**
/check 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU

**What the bot analyzes:**
- Direct transfers (SOL and tokens)
- Funding relationships
- Interaction frequency
- Transaction patterns

**Scoring factors:**
- Funder wallet (highest priority)
- Bidirectional transfers
- Frequent interactions
- Significant amounts

**Filtered out:**
- CEX addresses (Binance, Coinbase, etc.)
- DEX programs (Raydium, Jupiter, etc.)
- LP and pool addresses
- System programs
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /check command."""
    if not context.args:
        await update.message.reply_text(
            "Please provide a wallet address.\n"
            "Usage: /check <wallet_address>"
        )
        return

    address = context.args[0].strip()

    if not is_valid_solana_address(address):
        await update.message.reply_text(
            "Invalid Solana address format. "
            "Please provide a valid base58 address."
        )
        return

    # Send initial message
    status_msg = await update.message.reply_text(
        f"Analyzing wallet `{format_address(address)}`...\n"
        "This may take a moment.",
        parse_mode="Markdown"
    )

    try:
        results = await analyze_wallet(address)
        formatted = format_results(results)

        # Split message if too long (Telegram limit is 4096 chars)
        if len(formatted) > 4000:
            parts = [formatted[i:i+4000] for i in range(0, len(formatted), 4000)]
            await status_msg.edit_text(parts[0], parse_mode="Markdown")
            for part in parts[1:]:
                await update.message.reply_text(part, parse_mode="Markdown")
        else:
            await status_msg.edit_text(formatted, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error analyzing wallet {address}: {e}")
        await status_msg.edit_text(
            f"An error occurred while analyzing the wallet: {str(e)}"
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
    logger.info("Starting bot...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
