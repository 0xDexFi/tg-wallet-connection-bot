"""
Advanced wallet analysis engine with multi-heuristic scoring.
Implements techniques from ZachXBT, Chainalysis, and Bubblemaps.
"""

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any
from helius_client import helius_client
from filters import (
    filter_addresses,
    is_excluded_address,
    is_cex_address,
    get_cex_name,
)
from config import (
    SCORES,
    HOP1_TRANSACTION_LIMIT,
    HOP2_TRANSACTION_LIMIT,
    MAX_HOP1_WALLETS,
    MAX_HOP2_WALLETS,
    MIN_SOL_THRESHOLD,
    DUST_THRESHOLD,
)


# Known stablecoin mints (USDC, USDT, etc.)
STABLECOIN_MINTS = {
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
    "USDH1SM1ojwWUga67PGrgFWUHibbjqMvuMaDkRJTgkX": "USDH",
    "USDSwr9ApdHk5bvJKMjzff41FfuX8bSxdKcR81vTwcA": "USDS",
}


@dataclass
class WalletConnection:
    """Represents a connection to another wallet with scoring details."""
    address: str
    score: float = 0.0
    signals: list[str] = field(default_factory=list)

    # Interaction data
    sent_count: int = 0
    received_count: int = 0
    sent_sol: float = 0.0
    received_sol: float = 0.0
    sent_usd: float = 0.0  # USD value from stablecoins
    received_usd: float = 0.0  # USD value from stablecoins

    # Timing data
    first_interaction: int | None = None
    last_interaction: int | None = None
    active_hours: set = field(default_factory=set)

    # Relationship data
    is_funder: bool = False
    is_fee_payer: bool = False
    is_bidirectional: bool = False
    common_counterparties: int = 0
    cex_deposit_match: bool = False

    # Hop tracking
    hop_level: int = 1
    connected_via: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Complete analysis result for a wallet."""
    target_address: str
    transaction_count: int
    funder: str | None
    funder_of_funder: str | None

    # Connections by hop
    direct_connections: list[WalletConnection] = field(default_factory=list)
    hop2_connections: list[WalletConnection] = field(default_factory=list)

    # Cluster analysis
    same_funder_cluster: list[str] = field(default_factory=list)
    bidirectional_cluster: list[str] = field(default_factory=list)

    # Metadata
    error: str | None = None


def extract_wallet_interactions(
    transactions: list[dict],
    target_address: str,
) -> dict[str, WalletConnection]:
    """
    Extract all wallet interactions from transactions with detailed metadata.
    """
    connections: dict[str, WalletConnection] = defaultdict(
        lambda: WalletConnection(address="")
    )

    for tx in transactions:
        timestamp = tx.get("timestamp", 0)
        fee_payer = tx.get("feePayer", "")

        # Track hour of activity for timing correlation
        if timestamp:
            hour = (timestamp // 3600) % 24

        # Process native SOL transfers
        for transfer in tx.get("nativeTransfers", []):
            from_addr = transfer.get("fromUserAccount", "")
            to_addr = transfer.get("toUserAccount", "")
            amount = transfer.get("amount", 0) / 1e9  # lamports to SOL

            if from_addr == target_address and to_addr and to_addr != target_address:
                conn = connections[to_addr]
                conn.address = to_addr
                conn.sent_count += 1
                conn.sent_sol += amount
                _update_timing(conn, timestamp, hour if timestamp else None)

            elif to_addr == target_address and from_addr and from_addr != target_address:
                conn = connections[from_addr]
                conn.address = from_addr
                conn.received_count += 1
                conn.received_sol += amount
                _update_timing(conn, timestamp, hour if timestamp else None)

        # Process token transfers
        for transfer in tx.get("tokenTransfers", []):
            from_addr = transfer.get("fromUserAccount", "")
            to_addr = transfer.get("toUserAccount", "")
            mint = transfer.get("mint", "")
            token_amount = transfer.get("tokenAmount", 0)

            # Calculate USD value for stablecoins (1:1 with USD)
            usd_value = 0.0
            if mint in STABLECOIN_MINTS:
                usd_value = float(token_amount) if token_amount else 0.0

            if from_addr == target_address and to_addr and to_addr != target_address:
                conn = connections[to_addr]
                conn.address = to_addr
                conn.sent_count += 1
                conn.sent_usd += usd_value
                _update_timing(conn, timestamp, hour if timestamp else None)

            elif to_addr == target_address and from_addr and from_addr != target_address:
                conn = connections[from_addr]
                conn.address = from_addr
                conn.received_count += 1
                conn.received_usd += usd_value
                _update_timing(conn, timestamp, hour if timestamp else None)

        # Track fee payer relationships
        if fee_payer and fee_payer != target_address:
            conn = connections[fee_payer]
            conn.address = fee_payer
            conn.is_fee_payer = True
            _update_timing(conn, timestamp, hour if timestamp else None)

    # Mark bidirectional connections
    for conn in connections.values():
        if conn.sent_count > 0 and conn.received_count > 0:
            conn.is_bidirectional = True

    return dict(connections)


def _update_timing(conn: WalletConnection, timestamp: int, hour: int | None):
    """Update timing metadata for a connection."""
    if timestamp:
        if conn.first_interaction is None or timestamp < conn.first_interaction:
            conn.first_interaction = timestamp
        if conn.last_interaction is None or timestamp > conn.last_interaction:
            conn.last_interaction = timestamp
    if hour is not None:
        conn.active_hours.add(hour)


def find_funder(transactions: list[dict], target_address: str) -> str | None:
    """
    Find the wallet that first funded the target address.
    This is the strongest signal for wallet connection.
    """
    sorted_txs = sorted(transactions, key=lambda x: x.get("timestamp", float("inf")))

    for tx in sorted_txs:
        for transfer in tx.get("nativeTransfers", []):
            to_addr = transfer.get("toUserAccount", "")
            from_addr = transfer.get("fromUserAccount", "")
            amount = transfer.get("amount", 0)

            if to_addr == target_address and from_addr and amount > 0:
                if not is_excluded_address(from_addr):
                    return from_addr
    return None


def find_cex_deposits(transactions: list[dict], target_address: str) -> dict[str, list[str]]:
    """
    Find CEX deposit addresses used by the target.
    If another wallet uses the same deposit address = likely same owner.
    """
    cex_deposits: dict[str, list[str]] = defaultdict(list)

    for tx in transactions:
        for transfer in tx.get("nativeTransfers", []):
            from_addr = transfer.get("fromUserAccount", "")
            to_addr = transfer.get("toUserAccount", "")

            if from_addr == target_address and to_addr:
                cex_name = get_cex_name(to_addr)
                if cex_name:
                    cex_deposits[cex_name].append(to_addr)

    return dict(cex_deposits)


def calculate_timing_correlation(
    conn: WalletConnection,
    target_hours: set[int],
) -> float:
    """
    Calculate timing correlation score.
    Wallets active in the same hours are more likely same owner.
    """
    if not conn.active_hours or not target_hours:
        return 0.0

    overlap = len(conn.active_hours & target_hours)
    total = len(conn.active_hours | target_hours)

    if total == 0:
        return 0.0

    return overlap / total


def has_round_amounts(conn: WalletConnection) -> bool:
    """
    Check if transfers involve round numbers.
    Round number transfers suggest intentional/same-person transfers.
    """
    round_numbers = [0.1, 0.5, 1, 2, 5, 10, 25, 50, 100, 250, 500, 1000]

    for amount in [conn.sent_sol, conn.received_sol]:
        if amount > 0:
            for round_num in round_numbers:
                if abs(amount - round_num) < 0.001:
                    return True
                if round_num > 0 and abs(amount % round_num) < 0.001:
                    return True
    return False


def score_connection(
    conn: WalletConnection,
    funder: str | None,
    target_hours: set[int],
    target_counterparties: set[str],
) -> float:
    """
    Calculate comprehensive score for a wallet connection.
    Uses multiple heuristics weighted by signal strength.
    """
    score = 0.0
    signals = []

    # FUNDER - Highest priority signal
    if conn.address == funder:
        score += SCORES["FUNDER"]
        conn.is_funder = True
        signals.append("FUNDER")

    # FEE PAYER - Strong signal on Solana
    if conn.is_fee_payer:
        score += SCORES["FEE_PAYER"]
        signals.append("FEE_PAYER")

    # BIDIRECTIONAL - Two-way transfers indicate close relationship
    if conn.is_bidirectional:
        score += SCORES["BIDIRECTIONAL"]
        signals.append("BIDIRECTIONAL")

    # FREQUENCY - Multiple interactions
    total_interactions = conn.sent_count + conn.received_count
    if total_interactions >= 10:
        score += SCORES["HIGH_FREQUENCY"]
        signals.append("HIGH_FREQ")
    elif total_interactions >= 5:
        score += SCORES["MEDIUM_FREQUENCY"]
        signals.append("MED_FREQ")

    # ROUND AMOUNTS - Suggests intentional transfers
    if has_round_amounts(conn):
        score += SCORES["ROUND_AMOUNT"]
        signals.append("ROUND_AMT")

    # LARGE TRANSFERS - Significant amounts
    total_sol = conn.sent_sol + conn.received_sol
    if total_sol >= 10:
        score += SCORES["LARGE_TRANSFER"]
        signals.append("LARGE_XFER")

    # TIMING CORRELATION
    timing_score = calculate_timing_correlation(conn, target_hours)
    if timing_score > 0.5:
        score += SCORES["TIMING_CORRELATION"]
        signals.append("TIMING")

    # COMMON COUNTERPARTIES
    # (This is calculated separately and added to the connection)
    if conn.common_counterparties >= 5:
        score += SCORES["COMMON_COUNTERPARTY_HIGH"]
        signals.append("COMMON_CP_HIGH")
    elif conn.common_counterparties >= 3:
        score += SCORES["COMMON_COUNTERPARTY_MED"]
        signals.append("COMMON_CP")

    conn.score = score
    conn.signals = signals
    return score


def find_common_counterparties(
    target_counterparties: set[str],
    wallet_counterparties: set[str],
) -> int:
    """Count common counterparties between two wallets."""
    return len(target_counterparties & wallet_counterparties)


def get_total_usd_value(conn: WalletConnection, sol_price: float = 200.0) -> float:
    """
    Calculate total USD value of a connection.
    Includes SOL (converted at given price) + stablecoin transfers.
    """
    sol_value = (conn.sent_sol + conn.received_sol) * sol_price
    stable_value = conn.sent_usd + conn.received_usd
    return sol_value + stable_value


def is_spam_connection(conn: WalletConnection) -> bool:
    """
    Check if a connection is likely spam/dust.

    Spam indicators:
    - Very small total value (dust attacks)
    - Only received tiny amounts (airdrop spam)
    - No meaningful interaction pattern
    """
    total_sol = conn.sent_sol + conn.received_sol
    total_usd = conn.sent_usd + conn.received_usd
    total_value = get_total_usd_value(conn)

    # If total value is below $1, it's spam
    if total_value < 1.0:
        return True

    # If only received tiny amount (SOL or USD) and never sent, likely airdrop spam
    if conn.sent_count == 0:
        received_value = (conn.received_sol * 200.0) + conn.received_usd
        if received_value < 100.0:  # Less than $100 received only
            # Exception: if it's a fee payer, keep it
            if not conn.is_fee_payer:
                return True

    # If only sent tiny amount and never received, could be spam
    if conn.received_count == 0:
        sent_value = (conn.sent_sol * 200.0) + conn.sent_usd
        if sent_value < 1.0:  # Less than $1 sent
            return True

    return False


def filter_spam_connections(
    connections: dict[str, WalletConnection],
    funder: str | None = None,
    min_usd_value: float = 100.0,  # $100 minimum
) -> dict[str, WalletConnection]:
    """
    Filter out spam/dust connections while keeping important ones.

    Always keeps:
    - The funder (most important signal)
    - Fee payers (important for Solana analysis)
    - Bidirectional connections (strong signal)
    - Connections with significant value (SOL + stablecoins >= $100)
    """
    filtered = {}

    for addr, conn in connections.items():
        # Always keep the funder
        if funder and addr == funder:
            filtered[addr] = conn
            continue

        # Always keep fee payers
        if conn.is_fee_payer:
            filtered[addr] = conn
            continue

        # Always keep bidirectional connections
        if conn.is_bidirectional:
            filtered[addr] = conn
            continue

        # Check if it meets the minimum USD value threshold
        total_value = get_total_usd_value(conn)
        if total_value >= min_usd_value:
            filtered[addr] = conn
            continue

        # Check if it's not spam (for edge cases)
        if not is_spam_connection(conn):
            # Even if not spam, still require some minimum value
            if total_value >= 10.0:  # At least $10
                filtered[addr] = conn
                continue

    return filtered


async def analyze_hop2_wallet(
    wallet_addr: str,
    wallet_score: float,
    target_address: str,
    target_counterparties: set[str],
    funder: str | None,
) -> tuple[str, dict[str, WalletConnection]]:
    """Analyze a hop-1 wallet's connections for hop-2 analysis."""
    try:
        transactions = await helius_client.get_transaction_history(
            wallet_addr,
            limit=HOP2_TRANSACTION_LIMIT,
        )
        connections = extract_wallet_interactions(transactions, wallet_addr)
        filtered = filter_addresses(
            {addr: {"label": ""} for addr in connections.keys()}
        )

        # Keep only filtered connections
        hop2_connections = {
            addr: connections[addr]
            for addr in filtered.keys()
            if addr != target_address and addr in connections
        }

        # Check if this wallet shares the same funder
        hop1_funder = find_funder(transactions, wallet_addr)

        # Filter out spam/dust from hop2 connections
        hop2_connections = filter_spam_connections(hop2_connections, hop1_funder)

        for addr, conn in hop2_connections.items():
            conn.hop_level = 2
            conn.connected_via = [wallet_addr]

            # SAME FUNDER - Very strong signal
            if funder and hop1_funder and funder == hop1_funder:
                conn.score += SCORES["SAME_FUNDER"] * 0.5
                conn.signals.append("SAME_FUNDER_VIA")

            # Common counterparties with target
            wallet_cp = set(connections.keys())
            conn.common_counterparties = find_common_counterparties(
                target_counterparties, wallet_cp
            )

        return wallet_addr, hop2_connections

    except Exception:
        return wallet_addr, {}


async def analyze_wallet(address: str) -> AnalysisResult:
    """
    Comprehensive wallet analysis with multi-hop clustering.
    """
    result = AnalysisResult(
        target_address=address,
        transaction_count=0,
        funder=None,
        funder_of_funder=None,
    )

    # =========================================================================
    # PHASE 1: Fetch target wallet transactions
    # =========================================================================
    try:
        transactions = await helius_client.get_transaction_history(
            address, limit=HOP1_TRANSACTION_LIMIT
        )
    except Exception as e:
        result.error = f"Failed to fetch transactions: {str(e)}"
        return result

    if not transactions:
        result.error = "No transactions found for this address"
        return result

    result.transaction_count = len(transactions)

    # =========================================================================
    # PHASE 2: Extract direct connections
    # =========================================================================
    connections = extract_wallet_interactions(transactions, address)

    # Find the funder (highest priority signal)
    funder = find_funder(transactions, address)
    result.funder = funder

    # Get target's active hours for timing correlation
    target_hours: set[int] = set()
    for tx in transactions:
        ts = tx.get("timestamp", 0)
        if ts:
            target_hours.add((ts // 3600) % 24)

    # Get target's counterparties for common counterparty analysis
    target_counterparties = set(connections.keys())

    # =========================================================================
    # PHASE 3: Find funder's funder (for same-funder clustering)
    # =========================================================================
    funder_of_funder = None
    funder_siblings: list[str] = []

    if funder:
        try:
            funder_txs = await helius_client.get_transaction_history(
                funder, limit=50
            )
            funder_of_funder = find_funder(funder_txs, funder)
            result.funder_of_funder = funder_of_funder

            # Find other wallets funded by the same funder (with minimum threshold)
            funder_connections = extract_wallet_interactions(funder_txs, funder)
            for addr, conn in funder_connections.items():
                # Only include if sent meaningful amount (not dust)
                if conn.sent_count > 0 and conn.sent_sol >= MIN_SOL_THRESHOLD:
                    if addr != address and not is_excluded_address(addr):
                        funder_siblings.append(addr)

            result.same_funder_cluster = funder_siblings[:10]
        except Exception:
            pass

    # =========================================================================
    # PHASE 4: Score and filter direct connections
    # =========================================================================
    # First filter out known programs/exchanges/etc
    filtered_addrs = filter_addresses(
        {addr: {"label": ""} for addr in connections.keys()}
    )
    filtered_connections = {
        addr: connections[addr]
        for addr in filtered_addrs.keys()
        if addr in connections
    }

    # Then filter out spam/dust connections
    filtered_connections = filter_spam_connections(filtered_connections, funder)

    # Score each connection
    for addr, conn in filtered_connections.items():
        # Check for same-funder relationship
        if addr in funder_siblings:
            conn.score += SCORES["SAME_FUNDER"]
            conn.signals.append("SAME_FUNDER")

        score_connection(conn, funder, target_hours, target_counterparties)

    # Sort by score
    scored_connections = sorted(
        filtered_connections.values(),
        key=lambda x: x.score,
        reverse=True,
    )

    result.direct_connections = scored_connections[:MAX_HOP1_WALLETS]

    # Track bidirectional cluster
    result.bidirectional_cluster = [
        conn.address for conn in scored_connections if conn.is_bidirectional
    ][:10]

    # =========================================================================
    # PHASE 5: Hop-2 Analysis
    # =========================================================================
    top_wallets = [conn.address for conn in scored_connections[:MAX_HOP2_WALLETS]]

    hop2_tasks = [
        analyze_hop2_wallet(
            wallet_addr,
            filtered_connections.get(wallet_addr, WalletConnection(address=wallet_addr)).score,
            address,
            target_counterparties,
            funder,
        )
        for wallet_addr in top_wallets
    ]

    hop2_results = await asyncio.gather(*hop2_tasks, return_exceptions=True)

    # Aggregate hop-2 connections
    hop2_aggregated: dict[str, WalletConnection] = {}

    for res in hop2_results:
        if isinstance(res, Exception):
            continue
        via_wallet, hop2_conns = res
        for addr, conn in hop2_conns.items():
            if addr in filtered_connections:
                continue  # Skip if already a direct connection

            if addr not in hop2_aggregated:
                hop2_aggregated[addr] = conn
            else:
                existing = hop2_aggregated[addr]
                existing.score += conn.score * 0.5
                existing.connected_via.extend(conn.connected_via)
                existing.common_counterparties = max(
                    existing.common_counterparties,
                    conn.common_counterparties,
                )

    # Score and sort hop-2 connections
    sorted_hop2 = sorted(
        hop2_aggregated.values(),
        key=lambda x: x.score,
        reverse=True,
    )

    result.hop2_connections = sorted_hop2[:20]

    return result


def format_analysis_result(result: AnalysisResult) -> dict:
    """Convert analysis result to dictionary for JSON serialization."""
    if result.error:
        return {"error": result.error}

    return {
        "address": result.target_address,
        "transaction_count": result.transaction_count,
        "funder": result.funder,
        "funder_of_funder": result.funder_of_funder,
        "same_funder_cluster": result.same_funder_cluster,
        "bidirectional_cluster": result.bidirectional_cluster,
        "direct_connections": [
            {
                "address": conn.address,
                "score": round(conn.score, 1),
                "signals": conn.signals,
                "is_funder": conn.is_funder,
                "is_bidirectional": conn.is_bidirectional,
                "sent_count": conn.sent_count,
                "received_count": conn.received_count,
                "sent_sol": round(conn.sent_sol, 4),
                "received_sol": round(conn.received_sol, 4),
                "sent_usd": round(conn.sent_usd, 2),
                "received_usd": round(conn.received_usd, 2),
                "total_value_usd": round(get_total_usd_value(conn), 2),
            }
            for conn in result.direct_connections
        ],
        "hop2_connections": [
            {
                "address": conn.address,
                "score": round(conn.score, 1),
                "signals": conn.signals,
                "connected_via": conn.connected_via[:3],
                "common_counterparties": conn.common_counterparties,
            }
            for conn in result.hop2_connections
        ],
    }
