import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")
if not HELIUS_API_KEY:
    raise ValueError("HELIUS_API_KEY not set in environment")

HELIUS_BASE_URL = "https://api.helius.xyz/v0"
HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# Analysis settings
TRANSACTION_LIMIT = 500  # Max transactions to fetch for target wallet
HOP1_TRANSACTION_LIMIT = 500  # Increased for better coverage
HOP2_TRANSACTION_LIMIT = 100  # Keep lower for hop2 (many wallets)
MAX_HOP1_WALLETS = 30
MAX_HOP2_WALLETS = 15
MAX_CONCURRENT_REQUESTS = 5  # Reduced to avoid rate limits

# Spam/dust filtering thresholds
MIN_SOL_THRESHOLD = 0.5  # Minimum SOL value to consider (~$100 at $200/SOL)
MIN_USD_THRESHOLD = 100  # Minimum USD value to show connection
MIN_INTERACTION_COUNT = 1  # Minimum number of meaningful interactions
DUST_THRESHOLD = 0.01  # Below this is considered dust (spam) - increased from 0.001

# Scoring weights
SCORES = {
    "FUNDER": 100,
    "SAME_FUNDER": 90,
    "SAME_CEX_DEPOSIT": 95,
    "FEE_PAYER": 60,
    "BIDIRECTIONAL": 50,
    "ADDRESS_REUSE": 70,
    "COMMON_COUNTERPARTY_HIGH": 40,
    "COMMON_COUNTERPARTY_MED": 25,
    "TIMING_CORRELATION": 30,
    "ROUND_AMOUNT": 20,
    "HIGH_FREQUENCY": 25,
    "MEDIUM_FREQUENCY": 15,
    "LARGE_TRANSFER": 20,
    "LOOP_DETECTED": 60,
}
