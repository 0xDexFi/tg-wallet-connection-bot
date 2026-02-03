"""
Enhanced Helius API client for comprehensive Solana transaction data.
Supports transaction history, parsed transactions, and signatures.
"""

import asyncio
import httpx
from typing import Any
from config import HELIUS_API_KEY, HELIUS_BASE_URL, HELIUS_RPC_URL, MAX_CONCURRENT_REQUESTS


class HeliusClient:
    """Async client for Helius API with rate limiting."""

    def __init__(self):
        self.api_key = HELIUS_API_KEY
        self.base_url = HELIUS_BASE_URL
        self.rpc_url = HELIUS_RPC_URL
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def _request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        json_data: dict | None = None,
        timeout: float = 30.0,
    ) -> Any:
        """Make rate-limited HTTP request."""
        async with self._semaphore:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method == "GET":
                    response = await client.get(url, params=params)
                else:
                    response = await client.post(url, params=params, json=json_data)
                response.raise_for_status()
                return response.json()

    async def get_transaction_history(
        self,
        address: str,
        limit: int = 100,
        before: str | None = None,
    ) -> list[dict]:
        """
        Fetch parsed transaction history using Helius Enhanced Transactions API.
        Returns enriched transaction data with parsed instructions.
        """
        url = f"{self.base_url}/addresses/{address}/transactions"
        params = {
            "api-key": self.api_key,
            "limit": min(limit, 100),
        }
        if before:
            params["before"] = before

        try:
            return await self._request("GET", url, params=params)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                await asyncio.sleep(1)
                return await self._request("GET", url, params=params)
            raise

    async def get_all_transaction_history(
        self,
        address: str,
        max_transactions: int = 500,
    ) -> list[dict]:
        """
        Fetch multiple pages of transaction history.
        """
        all_transactions = []
        before = None

        while len(all_transactions) < max_transactions:
            batch = await self.get_transaction_history(
                address,
                limit=100,
                before=before,
            )
            if not batch:
                break

            all_transactions.extend(batch)

            if len(batch) < 100:
                break

            before = batch[-1].get("signature")
            await asyncio.sleep(0.1)  # Rate limit

        return all_transactions[:max_transactions]

    async def get_signatures_for_address(
        self,
        address: str,
        limit: int = 100,
    ) -> list[dict]:
        """
        Get transaction signatures for an address using RPC.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                address,
                {"limit": limit}
            ]
        }

        result = await self._request("POST", self.rpc_url, json_data=payload)
        return result.get("result", [])

    async def get_parsed_transaction(self, signature: str) -> dict | None:
        """
        Get parsed transaction details for a specific signature.
        """
        url = f"{self.base_url}/transactions"
        params = {"api-key": self.api_key}
        payload = {"transactions": [signature]}

        try:
            result = await self._request("POST", url, params=params, json_data=payload)
            return result[0] if result else None
        except Exception:
            return None

    async def get_parsed_transactions(self, signatures: list[str]) -> list[dict]:
        """
        Get parsed transaction details for multiple signatures.
        Max 100 per request.
        """
        if not signatures:
            return []

        url = f"{self.base_url}/transactions"
        params = {"api-key": self.api_key}
        payload = {"transactions": signatures[:100]}

        try:
            return await self._request("POST", url, params=params, json_data=payload)
        except Exception:
            return []

    async def get_token_accounts(self, address: str) -> list[dict]:
        """
        Get all token accounts owned by an address.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                address,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed"}
            ]
        }

        try:
            result = await self._request("POST", self.rpc_url, json_data=payload)
            return result.get("result", {}).get("value", [])
        except Exception:
            return []

    async def get_account_info(self, address: str) -> dict | None:
        """
        Get account info for an address.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [
                address,
                {"encoding": "jsonParsed"}
            ]
        }

        try:
            result = await self._request("POST", self.rpc_url, json_data=payload)
            return result.get("result", {}).get("value")
        except Exception:
            return None

    async def get_balance(self, address: str) -> int:
        """
        Get SOL balance in lamports.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address]
        }

        try:
            result = await self._request("POST", self.rpc_url, json_data=payload)
            return result.get("result", {}).get("value", 0)
        except Exception:
            return 0


# Singleton instance
helius_client = HeliusClient()
