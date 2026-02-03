"""Address filtering to exclude known exchanges, DEXs, LPs, and system programs."""

# Known CEX deposit/withdrawal addresses
CEX_ADDRESSES = {
    "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9": "Binance",
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Binance",
    "2ojv9BAiHUrvsm9gxDe7fJSzbNZSJcxZvf8dqmWGHG8S": "Binance",
    "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS": "Coinbase",
    "GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE": "Coinbase",
    "2AQdpHJ2JpcEgPiATUXjQxA8QmafFegfQwSLWSprPicm": "Coinbase",
    "6FEVkH17P9y8Q9aCkDdPcMDjvj7SVxrTETaYEm8f51S2": "Kraken",
    "CQfcwJwPjpKfgBTW8h1cHfU4VPHFJXVvRXNvyF6FLKAZ": "Kraken",
    "ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ": "OKX",
    "5VCwKtCXgCJ6kit5FybXjvriW3xELsFDhYrPSqtJNmcD": "OKX",
    "BmFdpraQhkiDQE6SnfG5omcA1VwzqfXrwtNYBwWTymy6": "Gate.io",
    "u6PJ8DtQuPFnfmwHbGFULQ4u4EgjDiyYKjVEsynXq2w": "Bybit",
    "AC5RDfQFmDS1deWZos921JfqscXdByf8BKHs5ACWjtW2": "Bybit",
}

# DEX and protocol program addresses
DEX_PROGRAMS = {
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium AMM",
    "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CLMM",
    "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM",
    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
    "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca Swap",
    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter v6",
    "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter v4",
    "jupoNjAxXgZ4rjzxzPMP4oxduvQsQtZzyknqvzYNrNu": "Jupiter Limit Order",
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "PumpFun",
    "PSwapMdSai8tjrEXcxFeQth87xC4rRsa4VA5mhGhXkP": "PumpSwap",
    "TSWAPaqyCSx2KABk68Shruf4rp7CxcNi8hAsbdwmHbN": "Tensor Swap",
    "TCMPhJdwDryooaGtiocG1u3xcYbRpiJzb283XfCZsDp": "Tensor cNFT",
    "M2mx93ekt1fmXSVkTrUL9xVFHkmME8HTUi5Cyc5aF7K": "Magic Eden v2",
    "CMZYPASGWeTz7RNGHaRJfCq2XQ5pYK6nDvVQxzkH51zb": "Magic Eden AMM",
}

# System programs and token programs
SYSTEM_PROGRAMS = {
    "11111111111111111111111111111111": "System Program",
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "Token Program",
    "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb": "Token-2022 Program",
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token Program",
    "ComputeBudget111111111111111111111111111111": "Compute Budget",
    "SysvarRent111111111111111111111111111111111": "Rent Sysvar",
    "SysvarC1ock11111111111111111111111111111111": "Clock Sysvar",
    "Vote111111111111111111111111111111111111111": "Vote Program",
    "Stake11111111111111111111111111111111111111": "Stake Program",
    "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s": "Metaplex Metadata",
    "auth9SigNpDKz4sJJ1DfCTuZrZNSAgh9sFD3rboVmgg": "Metaplex Auth",
    "noopb9bkMVfRPU8AsbpTUg8AQkHtKwMYZiFUjNRtMmV": "Noop Program",
}

# Fee and memo programs
OTHER_EXCLUDED = {
    "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr": "Memo Program",
    "Memo1UhkJRfHyvLMcVucJwxXeuD728EqVDDwQDxFMNo": "Memo Program v1",
}

# Combine all excluded addresses
EXCLUDED_ADDRESSES = {
    **CEX_ADDRESSES,
    **DEX_PROGRAMS,
    **SYSTEM_PROGRAMS,
    **OTHER_EXCLUDED,
}

# Patterns in address names/labels that indicate exclusion
EXCLUDED_PATTERNS = [
    "pump",
    "raydium",
    "orca",
    "jupiter",
    "serum",
    "openbook",
    "marinade",
    "lido",
    "jito",
]


def is_excluded_address(address: str) -> bool:
    """Check if address should be excluded."""
    return address in EXCLUDED_ADDRESSES


def get_exclusion_reason(address: str) -> str | None:
    """Get the reason why an address is excluded, or None if not excluded."""
    return EXCLUDED_ADDRESSES.get(address)


def is_program_address(address: str) -> bool:
    """
    Heuristic to check if address might be a program or PDA.
    Programs often end in specific patterns or are in our known lists.
    """
    if address in DEX_PROGRAMS or address in SYSTEM_PROGRAMS:
        return True
    # Most program addresses are 32-44 chars and end with specific patterns
    return False


def is_likely_lp_or_pool(address: str, label: str | None = None) -> bool:
    """Check if address is likely an LP token or pool address."""
    if label:
        label_lower = label.lower()
        for pattern in EXCLUDED_PATTERNS:
            if pattern in label_lower:
                return True
        if any(term in label_lower for term in ["pool", "lp", "liquidity", "vault"]):
            return True
    return False


def filter_addresses(addresses: dict[str, dict]) -> dict[str, dict]:
    """
    Filter out excluded addresses from the analysis results.

    Args:
        addresses: Dict mapping address -> metadata dict with interaction info

    Returns:
        Filtered dict with only potentially connected wallet addresses
    """
    filtered = {}
    for addr, data in addresses.items():
        if is_excluded_address(addr):
            continue
        if is_program_address(addr):
            continue
        label = data.get("label", "")
        if is_likely_lp_or_pool(addr, label):
            continue
        filtered[addr] = data
    return filtered
