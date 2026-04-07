"""ERC-8004 shared contract integration layer for Sepolia.

This module is intentionally thin and additive:
- it does not replace local trading logic
- it mirrors important lifecycle events onchain when configuration is available
- it degrades gracefully when RPC credentials or final ABIs are not present

The ABI fragments below are placeholders for the official hackathon contracts.
They are sufficient for wiring the backend flow and should be replaced with the
verified deployed ABIs when they are available.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from web3 import Web3

from app.config import settings
from app.services.wallet_service import wallet_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

SEPOLIA_CHAIN_ID = 11155111

AGENT_REGISTRY_ADDRESS = "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3"
HACKATHON_VAULT_ADDRESS = "0x0E7CD8ef9743FEcf94f9103033a044caBD45fC90"
RISK_ROUTER_ADDRESS = "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC"
REPUTATION_REGISTRY_ADDRESS = "0x423a9904e39537a9997fbaF0f220d79D7d545763"
VALIDATION_REGISTRY_ADDRESS = "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"

# Placeholder ABIs for the shared ERC-8004 hackathon contracts.
AGENT_REGISTRY_ABI: list[dict[str, Any]] = [
    {
        "inputs": [
            {"internalType": "string", "name": "agentName", "type": "string"},
            {"internalType": "address", "name": "wallet", "type": "address"},
            {"internalType": "string", "name": "metadata", "type": "string"},
        ],
        "name": "registerAgent",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "wallet", "type": "address"}],
        "name": "getAgentId",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

HACKATHON_VAULT_ABI: list[dict[str, Any]] = [
    {
        "inputs": [{"internalType": "uint256", "name": "agentId", "type": "uint256"}],
        "name": "claimAllocation",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

RISK_ROUTER_ABI: list[dict[str, Any]] = [
    {
        "inputs": [
            {"internalType": "string", "name": "asset", "type": "string"},
            {"internalType": "string", "name": "action", "type": "string"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "bytes", "name": "signature", "type": "bytes"},
        ],
        "name": "submitIntent",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

VALIDATION_REGISTRY_ABI: list[dict[str, Any]] = [
    {
        "inputs": [{"internalType": "bytes32", "name": "artifactHash", "type": "bytes32"}],
        "name": "postCheckpoint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]


class ERC8004Service:
    """Best-effort integration with the shared ERC-8004 contracts on Sepolia."""

    def __init__(self) -> None:
        self._web3: Web3 | None = None

    def _get_web3(self) -> Web3 | None:
        """Return a Web3 client when the RPC URL is configured and reachable."""
        if self._web3 is not None:
            return self._web3

        if not settings.sepolia_rpc_url:
            logger.warning("SEPOLIA_RPC_URL is not configured. Onchain sync disabled.")
            return None

        client = Web3(Web3.HTTPProvider(settings.sepolia_rpc_url))
        self._web3 = client
        return self._web3

    def _get_private_key(self) -> str:
        """Return the private key used for Sepolia transactions."""
        return settings.agent_private_key or wallet_service.load_wallet()["private_key"]

    def _contract(self, address: str, abi: list[dict[str, Any]]) -> Any | None:
        """Return a checksum-addressed contract instance when Web3 is configured."""
        web3 = self._get_web3()
        if web3 is None:
            return None
        return web3.eth.contract(address=web3.to_checksum_address(address), abi=abi)

    def _build_base_tx(self, web3: Web3, address: str) -> dict[str, Any]:
        """Build the common transaction envelope."""
        wallet = wallet_service.load_wallet()
        return {
            "from": wallet["address"],
            "nonce": web3.eth.get_transaction_count(wallet["address"]),
            "chainId": SEPOLIA_CHAIN_ID,
            "gas": 500000,
            "gasPrice": web3.eth.gas_price,
        }

    def _send_transaction(self, tx: dict[str, Any]) -> str:
        """Sign and broadcast a transaction, returning the transaction hash."""
        web3 = self._get_web3()
        if web3 is None:
            raise RuntimeError("Sepolia RPC is not configured.")
        signed = web3.eth.account.sign_transaction(tx, private_key=self._get_private_key())
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        return web3.to_hex(tx_hash)

    def register_agent(self, identity: Mapping[str, Any]) -> str | None:
        """Register the agent onchain and return the shared registry agent id.

        The identity JSON keeps its local UUID-style `agent_id`. The contract-level
        identifier is stored separately under `registry_agent_id` to avoid breaking
        existing API consumers.
        """

        existing_agent_id = identity.get("registry_agent_id")
        if existing_agent_id:
            return str(existing_agent_id)

        contract = self._contract(AGENT_REGISTRY_ADDRESS, AGENT_REGISTRY_ABI)
        web3 = self._get_web3()
        if contract is None or web3 is None:
            return None

        try:
            tx = contract.functions.registerAgent(
                str(identity["agent_name"]),
                web3.to_checksum_address(str(identity["wallet"])),
                str(identity.get("description", "")),
            ).build_transaction(self._build_base_tx(web3, AGENT_REGISTRY_ADDRESS))
            tx_hash = self._send_transaction(tx)
            logger.info("AgentRegistry registerAgent submitted | tx=%s", tx_hash)
            registry_agent_id = contract.functions.getAgentId(
                web3.to_checksum_address(str(identity["wallet"]))
            ).call()
            return str(registry_agent_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Agent registry sync failed: %s", exc)
            return None

    def claim_allocation(self, agent_id: str | int) -> str | None:
        """Claim the hackathon sandbox allocation for a registered agent."""
        contract = self._contract(HACKATHON_VAULT_ADDRESS, HACKATHON_VAULT_ABI)
        web3 = self._get_web3()
        if contract is None or web3 is None:
            return None

        try:
            tx = contract.functions.claimAllocation(int(agent_id)).build_transaction(
                self._build_base_tx(web3, HACKATHON_VAULT_ADDRESS)
            )
            tx_hash = self._send_transaction(tx)
            logger.info("HackathonVault claimAllocation submitted | agentId=%s tx=%s", agent_id, tx_hash)
            return tx_hash
        except Exception as exc:  # noqa: BLE001
            logger.warning("Sandbox allocation claim failed: %s", exc)
            return None

    def submit_trade_intent(self, intent: Mapping[str, Any], signature: str) -> str | None:
        """Submit an existing EIP-712 trade intent to the RiskRouter contract."""
        contract = self._contract(RISK_ROUTER_ADDRESS, RISK_ROUTER_ABI)
        web3 = self._get_web3()
        if contract is None or web3 is None:
            return None

        try:
            amount = int(round(float(intent["amount"]) * 1_000_000))
            tx = contract.functions.submitIntent(
                str(intent["asset"]),
                str(intent["action"]),
                amount,
                int(intent["timestamp"]),
                Web3.to_bytes(hexstr=signature),
            ).build_transaction(self._build_base_tx(web3, RISK_ROUTER_ADDRESS))
            tx_hash = self._send_transaction(tx)
            logger.info("RiskRouter submitIntent submitted | asset=%s action=%s tx=%s", intent["asset"], intent["action"], tx_hash)
            return tx_hash
        except Exception as exc:  # noqa: BLE001
            logger.warning("Trade intent submission failed: %s", exc)
            return None

    def post_validation_checkpoint(self, artifact_hash: str) -> str | None:
        """Publish a validation artifact hash to the ValidationRegistry contract."""
        contract = self._contract(VALIDATION_REGISTRY_ADDRESS, VALIDATION_REGISTRY_ABI)
        web3 = self._get_web3()
        if contract is None or web3 is None:
            return None

        try:
            tx = contract.functions.postCheckpoint(
                Web3.to_bytes(hexstr=artifact_hash)
            ).build_transaction(self._build_base_tx(web3, VALIDATION_REGISTRY_ADDRESS))
            tx_hash = self._send_transaction(tx)
            logger.info("ValidationRegistry checkpoint submitted | hash=%s tx=%s", artifact_hash, tx_hash)
            return tx_hash
        except Exception as exc:  # noqa: BLE001
            logger.warning("Validation checkpoint submission failed: %s", exc)
            return None


erc8004_service = ERC8004Service()
