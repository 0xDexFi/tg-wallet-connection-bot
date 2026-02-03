"""Core wallet analysis logic for finding connected wallets."""

import asyncio
from collections import defaultdict
from helius_client import helius_client
from filters import filter_addresses, is_excluded_address
from config import TRANSACTION_LIMIT, HOP2_TRANSACTION_LIMIT, MAX_HOP1_WALLETS


def extract_counterparties(
    transactions: list[dict], target_address: str
) -> dict[str, dict]:
    """
    Extract counterparty addresses from transactions.

    Args:
        transactions: List of parsed Helius transactions
        target_address: The address we're analyzing

    Returns:
        Dict mapping counterparty address -> interaction metadata
    """
    counterparties = defaultdict(lambda: {
        "sent_count": 0,
        "received_count": 0,
        "sent_sol": 0.0,
        "received_sol": 0.0,
        "first_interaction": None,
        "last_interaction": None,
        "is_funder": False,
    })

    for tx in transactions:
        timestamp = tx.get("timestamp", 0)
        tx_type = tx.get("type", "UNKNOWN")
        source = tx.get("source", "UNKNOWN")

        # Handle native transfers
        native_transfers = tx.get("nativeTransfers", [])
        for transfer in native_transfers:
            from_addr = transfer.get("fromUserAccount", "")
            to_addr = transfer.get("toUserAccount", "")
            amount = transfer.get("amount", 0) / 1e9  # Convert lamports to SOL

            if from_addr == target_address and to_addr and to_addr != target_address:
                # Target sent to this address
                cp = counterparties[to_addr]
                cp["sent_count"] += 1
                cp["sent_sol"] += amount
                _update_timestamps(cp, timestamp)

            elif to_addr == target_address and from_addr and from_addr != target_address:
                # Target received from this address
                cp = counterparties[from_addr]
                cp["received_count"] += 1
                cp["received_sol"] += amount
                _update_timestamps(cp, timestamp)

        # Handle token transfers
        token_transfers = tx.get("tokenTransfers", [])
        for transfer in token_transfers:
            from_addr = transfer.get("fromUserAccount", "")
            to_addr = transfer.get("toUserAccount", "")

            if from_addr == target_address and to_addr and to_addr != target_address:
                cp = counterparties[to_addr]
                cp["sent_count"] += 1
                _update_timestamps(cp, timestamp)

            elif to_addr == target_address and from_addr and from_addr != target_address:
                cp = counterparties[from_addr]
                cp["received_count"] += 1
                _update_timestamps(cp, timestamp)

        # Handle account data for other interaction types
        account_data = tx.get("accountData", [])
        for account in account_data:
            addr = account.get("account", "")
            if addr and addr != target_address:
                # Just track interaction exists
                cp = counterparties[addr]
                _update_timestamps(cp, timestamp)

    return dict(counterparties)


def _update_timestamps(cp: dict, timestamp: int):
    """Update first/last interaction timestamps."""
    if cp["first_interaction"] is None or timestamp < cp["first_interaction"]:
        cp["first_interaction"] = timestamp
    if cp["last_interaction"] is None or timestamp > cp["last_interaction"]:
        cp["last_interaction"] = timestamp


def find_funder(transactions: list[dict], target_address: str) -> str | None:
    """
    Find the wallet that first funded the target address.

    Args:
        transactions: List of parsed transactions (should be sorted by time)
        target_address: The address we're analyzing

    Returns:
        Address of the funder, or None if not found
    """
    # Sort by timestamp ascending to find earliest
    sorted_txs = sorted(transactions, key=lambda x: x.get("timestamp", float("inf")))

    for tx in sorted_txs:
        native_transfers = tx.get("nativeTransfers", [])
        for transfer in native_transfers:
            to_addr = transfer.get("toUserAccount", "")
            from_addr = transfer.get("fromUserAccount", "")
            amount = transfer.get("amount", 0)

            if to_addr == target_address and from_addr and amount > 0:
                if not is_excluded_address(from_addr):
                    return from_addr

    return None


def score_connections(
    counterparties: dict[str, dict],
    funder: str | None = None
) -> list[tuple[str, dict, float]]:
    """
    Score and rank connections by likelihood of being same person.

    Args:
        counterparties: Dict of counterparty address -> metadata
        funder: Address of the funder (if found)

    Returns:
        List of (address, metadata, score) tuples, sorted by score descending
    """
    scored = []

    for addr, data in counterparties.items():
        score = 0.0

        # Funder gets highest priority
        if addr == funder:
            score += 100.0
            data["is_funder"] = True

        # Frequent interactions
        total_interactions = data["sent_count"] + data["received_count"]
        score += min(total_interactions * 5, 30)  # Cap at 30 points

        # Bidirectional transfers (both sent and received)
        if data["sent_count"] > 0 and data["received_count"] > 0:
            score += 20.0

        # Significant SOL amounts
        total_sol = data["sent_sol"] + data["received_sol"]
        if total_sol > 10:
            score += 15.0
        elif total_sol > 1:
            score += 10.0
        elif total_sol > 0.1:
            score += 5.0

        # Round number transfers (suggests intentional, not fees)
        if _has_round_transfers(data):
            score += 10.0

        scored.append((addr, data, score))

    # Sort by score descending
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored


def _has_round_transfers(data: dict) -> bool:
    """Check if transfers involve round numbers (suggests same person)."""
    for amount in [data["sent_sol"], data["received_sol"]]:
        if amount > 0:
            # Check if close to a round number
            for round_num in [0.1, 0.5, 1, 2, 5, 10, 25, 50, 100]:
                if abs(amount - round_num) < 0.01:
                    return True
                if abs(amount % round_num) < 0.01:
                    return True
    return False


async def analyze_wallet(address: str) -> dict:
    """
    Analyze a wallet to find potentially connected wallets.

    Args:
        address: Solana wallet address to analyze

    Returns:
        Dict containing analysis results
    """
    # Hop 1: Get direct connections
    try:
        transactions = await helius_client.get_transaction_history(
            address, limit=TRANSACTION_LIMIT
        )
    except Exception as e:
        return {"error": f"Failed to fetch transactions: {str(e)}"}

    if not transactions:
        return {"error": "No transactions found for this address"}

    # Extract counterparties
    direct_connections = extract_counterparties(transactions, address)

    # Find funder
    funder = find_funder(transactions, address)

    # Filter out excluded addresses
    filtered_direct = filter_addresses(direct_connections)

    # Score and rank direct connections
    scored_direct = score_connections(filtered_direct, funder)

    # Take top connections for hop 2
    top_direct = scored_direct[:MAX_HOP1_WALLETS]

    # Hop 2: Analyze connections of top connections
    hop2_connections = defaultdict(lambda: {
        "connected_via": [],
        "total_score": 0.0,
    })

    async def fetch_hop2(wallet_addr: str, wallet_score: float):
        """Fetch and process hop 2 connections for a wallet."""
        try:
            hop2_txs = await helius_client.get_transaction_history(
                wallet_addr, limit=HOP2_TRANSACTION_LIMIT
            )
            hop2_counterparties = extract_counterparties(hop2_txs, wallet_addr)
            hop2_filtered = filter_addresses(hop2_counterparties)

            for addr, data in hop2_filtered.items():
                if addr != address:  # Don't include target in hop2
                    hop2_connections[addr]["connected_via"].append({
                        "wallet": wallet_addr,
                        "score": wallet_score,
                    })
                    # Add weighted score based on intermediate wallet's score
                    hop2_connections[addr]["total_score"] += wallet_score * 0.3
        except Exception:
            pass  # Silently skip failed hop2 fetches

    # Fetch hop 2 in parallel
    tasks = [
        fetch_hop2(addr, score)
        for addr, _, score in top_direct
    ]
    await asyncio.gather(*tasks)

    # Remove direct connections from hop2 (they're already in hop1)
    for addr, _, _ in scored_direct:
        hop2_connections.pop(addr, None)

    # Sort hop2 by total score
    sorted_hop2 = sorted(
        hop2_connections.items(),
        key=lambda x: x[1]["total_score"],
        reverse=True
    )[:20]  # Top 20 hop2 connections

    return {
        "address": address,
        "transaction_count": len(transactions),
        "funder": funder,
        "direct_connections": [
            {
                "address": addr,
                "score": score,
                "is_funder": data.get("is_funder", False),
                "sent_count": data["sent_count"],
                "received_count": data["received_count"],
                "sent_sol": round(data["sent_sol"], 4),
                "received_sol": round(data["received_sol"], 4),
            }
            for addr, data, score in scored_direct[:15]  # Top 15 direct
        ],
        "hop2_connections": [
            {
                "address": addr,
                "score": round(data["total_score"], 2),
                "connected_via": data["connected_via"],
            }
            for addr, data in sorted_hop2[:10]  # Top 10 hop2
        ],
    }
