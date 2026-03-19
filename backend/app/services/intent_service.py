"""Trade intent creation, signing, and verification service."""

import json
from time import time
from typing import TypedDict

from eth_account import Account
from eth_account.messages import encode_defunct

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

    def _serialize_intent(self, intent: TradeIntent) -> str:
        """Return stable JSON serialization for signing/recovery."""
        return json.dumps(intent, sort_keys=True, separators=(",", ":"))

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
        """Sign a trade intent using the agent wallet private key."""
        serialized = self._serialize_intent(intent)
        signature = wallet_service.sign_message(serialized)
        logger.info("Intent signed | wallet=%s", intent["wallet"])
        return signature

    def verify_signature(self, intent: TradeIntent, signature: str) -> bool:
        """Verify that signature matches the intent wallet address."""
        serialized = self._serialize_intent(intent)
        signable = encode_defunct(text=serialized)
        recovered = Account.recover_message(signable, signature=signature)
        return recovered.lower() == intent["wallet"].lower()


intent_service = IntentService()
