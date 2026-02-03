"""
Comprehensive address filtering for Solana wallet analysis.
Excludes CEXs, DEXs, LPs, protocols, system programs, and known entities.
"""

# ============================================================================
# CENTRALIZED EXCHANGES (CEX)
# ============================================================================
CEX_ADDRESSES = {
    # Binance
    "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9": "Binance",
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Binance",
    "2ojv9BAiHUrvsm9gxDe7fJSzbNZSJcxZvf8dqmWGHG8S": "Binance",
    "CVJVpeanE2Z96qEMjyFNrQe4MHH9FQMDWyQH4K3Vuqua": "Binance",
    "AC5RDfQFmDS1deWZos921JfqscXdByf8BKHs5ACWjtW2": "Binance",
    "9un5wqE3q4oCjyrDkwsdD48KteCJitQX5978Vh7KKxHo": "Binance",
    "HNAafKrJziFbqkCYMTFBXwhfVcAr6c2jPCdscNBnHHZP": "Binance",
    "7LbpuNPFwYyFVPGYzgPPWMJj8JcQzU9X7xWM5gqZ8xwM": "Binance",
    # Coinbase
    "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS": "Coinbase",
    "GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE": "Coinbase",
    "2AQdpHJ2JpcEgPiATUXjQxA8QmafFegfQwSLWSprPicm": "Coinbase",
    "5VCwKtCXgCJ6kit5FybXjvriW3xELsFDhYrPSqtJNmcD": "Coinbase",
    # Kraken
    "6FEVkH17P9y8Q9aCkDdPcMDjvj7SVxrTETaYEm8f51S2": "Kraken",
    "CQfcwJwPjpKfgBTW8h1cHfU4VPHFJXVvRXNvyF6FLKAZ": "Kraken",
    "CU1RD4K7sRRj5cpMJKofpgBJvC6mmUAD6P1y9cXA2YYT": "Kraken",
    # OKX
    "ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ": "OKX",
    "5VCwKtCXgCJ6kit5FybXjvriW3xELsFDhYrPSqtJNmcD": "OKX",
    "6Gmfq1YpEjRghEjfuYgqnVqjS4eCb8XwGYNBuDGskmQN": "OKX",
    # Bybit
    "u6PJ8DtQuPFnfmwHbGFULQ4u4EgjDiyYKjVEsynXq2w": "Bybit",
    "AC5RDfQFmDS1deWZos921JfqscXdByf8BKHs5ACWjtW2": "Bybit",
    # Gate.io
    "BmFdpraQhkiDQE6SnfG5omcA1VwzqfXrwtNYBwWTymy6": "Gate.io",
    "u6PJ8DtQuPFnfmwHbGFULQ4u4EgjDiyYKjVEsynXq2w": "Gate.io",
    # KuCoin
    "BQoU43k9dNPqBCjRJ8v8VxJPT5WVbfL7iN4vCNm5dXdW": "KuCoin",
    # Crypto.com
    "AobVSwdW9BbpMdJvTqeCN4hPAmh4rHm7vwLnQ5ATSPo9": "Crypto.com",
    # Huobi/HTX
    "88xTWZMeKfiTgbfEmPLdsUCQcZinwUfk25EBQZ21XMAZ": "Huobi",
    # FTX (defunct but still filter)
    "GXMaB6jm5cdoXRvzPK6SU5kYLNgE5qTqSHVMjMqQCaRv": "FTX",
}

# ============================================================================
# DEX PROGRAMS & AGGREGATORS
# ============================================================================
DEX_PROGRAMS = {
    # Raydium
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium AMM",
    "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CLMM",
    "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM",
    "routeUGWgWzqBWFcrCfv8tritsqukccJPu3q5GPP3xS": "Raydium Route",
    "27haf8L6oxUeXrHrgEgsexjSY5hbVUWEmvv9Nyxg8vQv": "Raydium V4",
    "5quBtoiQqxF9Jv6KYKctB59NT3gtJD2Y65kdnB1Uev3h": "Raydium Authority",
    # Jupiter
    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter v6",
    "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter v4",
    "JUP3c2Uh3WA4Ng34tw6kPd2G4C5BB21Xo36Je1s32Ph": "Jupiter v3",
    "JUP2jxvXaqu7NQY1GmNF4m1vodw12LVXYxbFL2uJvfo": "Jupiter v2",
    "jupoNjAxXgZ4rjzxzPMP4oxduvQsQtZzyknqvzYNrNu": "Jupiter Limit",
    "DCA265Vj8a9CEuX1eb1LWRnDT7uK6q1xMipnNyatn23M": "Jupiter DCA",
    "PERPHjGBqRHArX4DySjwM6UJHiR3sWAatqfdBS2qQJu": "Jupiter Perps",
    # Orca
    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
    "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca Swap",
    "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Orca",
    # PumpFun
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "PumpFun",
    "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1": "PumpFun Fee",
    # PumpSwap
    "PSwapMdSai8tjrEXcxFeQth87xC4rRsa4VA5mhGhXkP": "PumpSwap",
    # Meteora
    "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo": "Meteora DLMM",
    "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB": "Meteora Pools",
    # Lifinity
    "EewxydAPCCVuNEyrVN68PuSYdQ7wKn27V9Gjeoi8dy3S": "Lifinity",
    # Phoenix
    "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
    # OpenBook
    "opnb2LAfJYbRMAHHvqjCwQxanZn7ReEHp1k81EohpZb": "OpenBook",
    "srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX": "Serum",
}

# ============================================================================
# NFT MARKETPLACES & PROTOCOLS
# ============================================================================
NFT_PROGRAMS = {
    # Tensor
    "TSWAPaqyCSx2KABk68Shruf4rp7CxcNi8hAsbdwmHbN": "Tensor Swap",
    "TCMPhJdwDryooaGtiocG1u3xcYbRpiJzb283XfCZsDp": "Tensor cNFT",
    "TL1ST2iRBzuGTqLn1KXnGdSnEow62BzPnGiqyRXhWtW": "Tensorian",
    "4zdNGgAtFsW1cQgHqkiWyRsxaAgxrSRRynnuunxzjxue": "Tensor Bid",
    # Magic Eden
    "M2mx93ekt1fmXSVkTrUL9xVFHkmME8HTUi5Cyc5aF7K": "Magic Eden v2",
    "CMZYPASGWeTz7RNGHaRJfCq2XQ5pYK6nDvVQxzkH51zb": "Magic Eden AMM",
    "MEisE1HzehtrDpAAT8PnLHjpSSkRYakotTuJRPjTpo8": "Magic Eden",
    "mmm3XBJg5gk8XJxEKBvdgptZz6SgK4tXvn36sodowMc": "ME Launchpad",
    "hausS13jsjafwWwGqZTUQRmWyvyxn9EQpqMwV1PBBmk": "Magic Eden Haus",
    # Metaplex
    "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s": "Metaplex Metadata",
    "auth9SigNpDKz4sJJ1DfCTuZrZNSAgh9sFD3rboVmgg": "Metaplex Auth",
    "BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY": "Bubblegum",
    "cmtDvXumGCrqC1Age74AVPhSRVXJMd8PJS91L8KbNCK": "Compression",
    # Solanart
    "CJsLwbP1iu5DuUikHEJnLfANgKy6stB2uFgvBBHoyxwz": "Solanart",
}

# ============================================================================
# DEFI PROTOCOLS
# ============================================================================
DEFI_PROGRAMS = {
    # Marinade
    "MarBmsSgKXdrN1egZf5sqe1TMai9K1rChYNDJgjq7aD": "Marinade",
    "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So": "mSOL Token",
    # Lido
    "CrX7kMhLC3cSsXJdT7JDgqrRVWGnUpX3gfEfxxU2NVLi": "Lido",
    "stSoLwThyF3rJAWFAZeZ7F9CfNFNQxdD3jvV1uKq3jk": "stSOL Token",
    # Jito
    "Jito4APyf642JPZPx3hGc6WWJ8zPKtRbRs4P815Awbb": "Jito Stake",
    "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn": "jitoSOL Token",
    # Solend
    "So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo": "Solend",
    # Drift
    "dRiftyHA39MWEi3m9aunc5MzRF1JYuBsbn6VPcn33UH": "Drift",
    # Mango
    "4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg": "Mango",
    # Marginfi
    "MFv2hWf31Z9kbCa1snEPYctwafyhdvnV7FZnsebVacA": "Marginfi",
    # Kamino
    "KLend2g3cP87ber41GdPqBUKqvnMpKMzTw4wBpmAdQV": "Kamino Lend",
    "6LtLpnUFNByNXLyCoK9wA2MykKAmQNZKBdY8s47dehDc": "Kamino",
}

# ============================================================================
# SYSTEM PROGRAMS
# ============================================================================
SYSTEM_PROGRAMS = {
    "11111111111111111111111111111111": "System Program",
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "Token Program",
    "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb": "Token-2022",
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "ATA Program",
    "ComputeBudget111111111111111111111111111111": "Compute Budget",
    "SysvarRent111111111111111111111111111111111": "Rent Sysvar",
    "SysvarC1ock11111111111111111111111111111111": "Clock Sysvar",
    "SysvarS1otHashes111111111111111111111111111": "Slot Hashes",
    "SysvarRecentB1ockHashes11111111111111111111": "Recent Blockhashes",
    "Vote111111111111111111111111111111111111111": "Vote Program",
    "Stake11111111111111111111111111111111111111": "Stake Program",
    "Config1111111111111111111111111111111111111": "Config Program",
    "BPFLoader2111111111111111111111111111111111": "BPF Loader",
    "BPFLoaderUpgradeab1e11111111111111111111111": "Upgradeable Loader",
    "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr": "Memo Program",
    "Memo1UhkJRfHyvLMcVucJwxXeuD728EqVDDwQDxFMNo": "Memo v1",
    "noopb9bkMVfRPU8AsbpTUg8AQkHtKwMYZiFUjNRtMmV": "Noop Program",
    "AddressLookupTab1e1111111111111111111111111": "Address Lookup",
}

# ============================================================================
# BRIDGES & CROSS-CHAIN
# ============================================================================
BRIDGE_PROGRAMS = {
    "wormDTUJ6AWPNvk59vGQbDvGJmqbDTdgWgAqcLBCgUb": "Wormhole",
    "WnFt12ZrnzZrFZkt2xsNsaNWoQribnuQ5B5FrDbwDhD": "Wormhole NFT",
    "3u8hJUVTA4jH1wYAyUur7FFZVQ8H635K3tSHHF4ssjQ5": "Wormhole Bridge",
    "DeBridgeSo1111111111111111111111111111111111": "deBridge",
    "br1xwubggTiEZ6b7iNZUwfA3psygFfaXGfZ1heaN9AW": "Allbridge",
}

# ============================================================================
# KNOWN BOTS & MEV
# ============================================================================
BOT_ADDRESSES = {
    "JitoMEV1111111111111111111111111111111111111": "Jito MEV",
}

# Combine all excluded addresses
EXCLUDED_ADDRESSES = {
    **CEX_ADDRESSES,
    **DEX_PROGRAMS,
    **NFT_PROGRAMS,
    **DEFI_PROGRAMS,
    **SYSTEM_PROGRAMS,
    **BRIDGE_PROGRAMS,
    **BOT_ADDRESSES,
}

# Patterns in labels that indicate exclusion
EXCLUDED_LABEL_PATTERNS = [
    "pump", "raydium", "orca", "jupiter", "serum", "openbook",
    "marinade", "lido", "jito", "solend", "drift", "mango",
    "tensor", "magic eden", "metaplex", "pool", "lp ", "liquidity",
    "vault", "authority", "fee", "treasury", "program",
    "wormhole", "bridge", "swap", "amm", "dex",
]

# Known program ID prefixes (programs often start with these)
PROGRAM_PREFIXES = [
    "1111111111",  # System-like
    "So1",  # Solana protocols
    "Token",  # Token programs
]


def is_excluded_address(address: str) -> bool:
    """Check if address should be excluded from analysis."""
    return address in EXCLUDED_ADDRESSES


def get_exclusion_reason(address: str) -> str | None:
    """Get the reason why an address is excluded."""
    return EXCLUDED_ADDRESSES.get(address)


def is_likely_program(address: str) -> bool:
    """Heuristic check if address is likely a program."""
    if address in EXCLUDED_ADDRESSES:
        return True
    for prefix in PROGRAM_PREFIXES:
        if address.startswith(prefix):
            return True
    # Programs often have many 1s in them
    if address.count("1") > 10:
        return True
    return False


def is_excluded_by_label(label: str | None) -> bool:
    """Check if a label indicates the address should be excluded."""
    if not label:
        return False
    label_lower = label.lower()
    return any(pattern in label_lower for pattern in EXCLUDED_LABEL_PATTERNS)


def filter_addresses(addresses: dict[str, dict]) -> dict[str, dict]:
    """Filter out excluded addresses."""
    filtered = {}
    for addr, data in addresses.items():
        if is_excluded_address(addr):
            continue
        if is_likely_program(addr):
            continue
        label = data.get("label", "")
        if is_excluded_by_label(label):
            continue
        filtered[addr] = data
    return filtered


def get_cex_name(address: str) -> str | None:
    """Get CEX name if address belongs to a known CEX."""
    return CEX_ADDRESSES.get(address)


def is_cex_address(address: str) -> bool:
    """Check if address is a known CEX address."""
    return address in CEX_ADDRESSES
