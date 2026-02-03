import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")
if not HELIUS_API_KEY:
    raise ValueError("HELIUS_API_KEY not set in environment")

HELIUS_BASE_URL = f"https://api.helius.xyz/v0"
TRANSACTION_LIMIT = 100
HOP2_TRANSACTION_LIMIT = 50
MAX_HOP1_WALLETS = 20
