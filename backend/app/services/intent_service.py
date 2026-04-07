"""Trade intent creation, signing, and verification service."""

import json
from time import time
from typing import Any, TypedDict

from eth_account import Account
from eth_account.messages import encode_defunct, encode_typed_data

from app.services.erc8004_service import erc8004_service
from app.services.wallet_service import wallet_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TradeIntent(TypedDict):
    """Canonical trade intent payload emitted by strategy execution."""

    agent: str
    wallet: str
    asset: str
    action: str
    amount: float
    timestamp: int


class IntentService:
    """Create and sign verifiable decentralized trade intents."""

    _domain = {
        "name": "AutoHedgeAI",
        "version": "1",
        "chainId": 11155111,
    }
    _types = {
        "TradeIntent": [
            {"name": "asset", "type": "string"},
            {"name": "action", "type": "string"},
            {"name": "amount", "type": "uint256"},
            {"name": "timestamp", "type": "uint256"},
        ]
    }

    def _serialize_intent(self, intent: TradeIntent) -> str:
        """Return stable JSON serialization for signing/recovery."""
        return json.dumps(intent, sort_keys=True, separators=(",", ":"))

    def _build_eip712_payload(self, intent: TradeIntent) -> dict[str, Any]:
        """Return ERC-8004-compatible EIP-712 typed trade intent payload."""
        message = {
            "asset": intent["asset"],
            "action": intent["action"],
            "amount": int(round(intent["amount"] * 1_000_000)),
            "timestamp": intent["timestamp"],
        }
        return {
            "domain": dict(self._domain),
            "types": dict(self._types),
            "message": message,
        }

    def create_intent(
        self,
        agent: str,
        wallet: str,
        asset: str,
        action: str,
        amount: float,
    ) -> TradeIntent:
        """Construct a normalized trade intent payload."""
        intent: TradeIntent = {
            "agent": agent.strip(),
            "wallet": wallet.strip(),
            "asset": asset.strip().upper(),
            "action": action.strip().upper(),
            "amount": round(float(amount), 10),
            "timestamp": int(time()),
        }
        logger.info(
            "Trade intent created | agent=%s asset=%s action=%s amount=%s",
            intent["agent"],
            intent["asset"],
            intent["action"],
            intent["amount"],
        )
        return intent

    def sign_intent(self, intent: TradeIntent) -> str:
        """Sign a trade intent using EIP-712 typed data."""
        payload = self._build_eip712_payload(intent)
        wallet = wallet_service.load_wallet()
        signable = encode_typed_data(
            domain_data=payload["domain"],
            message_types=payload["types"],
            message_data=payload["message"],
        )
        signed = Account.sign_message(signable, private_key=wallet["private_key"])
        signature = signed.signature.hex()
        logger.info("Intent signed | wallet=%s", intent["wallet"])
        erc8004_service.submit_trade_intent(intent, signature)
        return signature

    def verify_signature(self, intent: TradeIntent, signature: str) -> bool:
        """Verify that signature matches the intent wallet using EIP-712 data."""
        payload = self._build_eip712_payload(intent)
        signable = encode_typed_data(
            domain_data=payload["domain"],
            message_types=payload["types"],
            message_data=payload["message"],
        )
        try:
            recovered = Account.recover_message(signable, signature=signature)
        except Exception:  # noqa: BLE001
            return False
        return recovered.lower() == intent["wallet"].lower()

    def create_signed_intent(
        self,
        agent: str,
        wallet: str,
        asset: str,
        action: str,
        amount: float,
    ) -> dict[str, Any]:
        """Create and sign an ERC-8004-compatible EIP-712 trade intent bundle."""
        intent = self.create_intent(agent, wallet, asset, action, amount)
        payload = self._build_eip712_payload(intent)
        signature = self.sign_intent(intent)
        return {
            "intent": payload["message"],
            "signature": signature,
            "domain": payload["domain"],
            "types": payload["types"],
        }


intent_service = IntentService()
