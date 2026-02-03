"""Helius API client for fetching Solana transaction data."""

import httpx
from config import HELIUS_API_KEY, HELIUS_BASE_URL


class HeliusClient:
    """Async client for Helius API."""

    def __init__(self):
        self.api_key = HELIUS_API_KEY
        self.base_url = HELIUS_BASE_URL

    async def get_transaction_history(
        self, address: str, limit: int = 100
    ) -> list[dict]:
        """
        Fetch parsed transaction history for an address using Helius Enhanced API.

        Args:
            address: Solana wallet address
            limit: Maximum number of transactions to fetch (max 100 per request)

        Returns:
            List of parsed transaction objects
        """
        url = f"{self.base_url}/addresses/{address}/transactions"
        params = {
            "api-key": self.api_key,
            "limit": min(limit, 100),
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def get_parsed_transactions(
        self, signatures: list[str]
    ) -> list[dict]:
        """
        Get parsed transaction details for specific signatures.

        Args:
            signatures: List of transaction signatures

        Returns:
            List of parsed transaction objects
        """
        url = f"{self.base_url}/transactions"
        params = {"api-key": self.api_key}
        payload = {"transactions": signatures}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, params=params, json=payload)
            response.raise_for_status()
            return response.json()

    async def get_balances(self, address: str) -> dict:
        """
        Get token balances for an address.

        Args:
            address: Solana wallet address

        Returns:
            Balance information
        """
        url = f"{self.base_url}/addresses/{address}/balances"
        params = {"api-key": self.api_key}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()


# Singleton instance
helius_client = HeliusClient()
