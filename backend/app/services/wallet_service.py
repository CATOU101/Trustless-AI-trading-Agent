"""Wallet service for creating and signing with the autonomous agent wallet."""

import json
from pathlib import Path
from typing import TypedDict

from eth_account import Account
from eth_account.messages import encode_defunct

from app.utils.logger import get_logger

logger = get_logger(__name__)


class AgentWallet(TypedDict):
    """Wallet persisted to disk for autonomous trading identity."""

    address: str
    private_key: str


class WalletService:
    """Create/load an Ethereum wallet and sign payloads."""

    _wallet_path = Path(__file__).resolve().parents[1] / "agent_wallet.json"

    def __init__(self) -> None:
        """Initialize wallet cache."""
        self._wallet: AgentWallet | None = None

    def create_wallet(self) -> AgentWallet:
        """Create a new wallet and persist it to disk."""
        account = Account.create()
        private_key = account.key.hex()
        if not private_key.startswith("0x"):
            private_key = f"0x{private_key}"

        wallet: AgentWallet = {
            "address": account.address,
            "private_key": private_key,
        }
        self._wallet_path.write_text(
            json.dumps(wallet, indent=2),
            encoding="utf-8",
        )
        self._wallet = wallet
        logger.info("Wallet loaded: %s", wallet["address"])
        return wallet

    def load_wallet(self) -> AgentWallet:
        """Load wallet from disk, creating one if it does not exist."""
        if self._wallet is not None:
            return self._wallet

        if not self._wallet_path.exists():
            logger.info("Wallet file missing. Creating a new agent wallet.")
            return self.create_wallet()

        payload = json.loads(self._wallet_path.read_text(encoding="utf-8"))
        raw_private_key = str(payload.get("private_key", "")).strip()
        if not raw_private_key:
            logger.warning("Wallet file is missing private key. Regenerating wallet.")
            return self.create_wallet()

        account = Account.from_key(raw_private_key)
        wallet: AgentWallet = {
            "address": account.address,
            "private_key": raw_private_key,
        }
        self._wallet = wallet

        if str(payload.get("address", "")).lower() != account.address.lower():
            self._wallet_path.write_text(
                json.dumps(wallet, indent=2),
                encoding="utf-8",
            )

        logger.info("Wallet loaded: %s", wallet["address"])
        return wallet

    def get_wallet_address(self) -> str:
        """Return the currently active agent wallet address."""
        return self.load_wallet()["address"]

    def sign_message(self, message: str) -> str:
        """Sign arbitrary UTF-8 text with the agent wallet."""
        wallet = self.load_wallet()
        signable = encode_defunct(text=message)
        signed_message = Account.sign_message(
            signable,
            private_key=wallet["private_key"],
        )
        return signed_message.signature.hex()


wallet_service = WalletService()
