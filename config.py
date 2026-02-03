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
TRANSACTION_LIMIT = 100
HOP1_TRANSACTION_LIMIT = 100
HOP2_TRANSACTION_LIMIT = 50
MAX_HOP1_WALLETS = 30
MAX_HOP2_WALLETS = 15
MAX_CONCURRENT_REQUESTS = 10

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
