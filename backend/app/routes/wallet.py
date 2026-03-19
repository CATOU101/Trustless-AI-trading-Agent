"""Wallet API routes."""

from fastapi import APIRouter

from app.services.trading_service import trading_service
from app.services.wallet_service import wallet_service

router = APIRouter(tags=["wallet"])


@router.get("/wallet")
async def get_wallet() -> dict[str, object]:
    """Return the agent wallet address and current cash balance."""
    portfolio = trading_service.get_portfolio()
    return {
        "address": wallet_service.get_wallet_address(),
        "balance": portfolio["cash_balance"],
    }


@router.get("/wallet/address")
async def get_wallet_address() -> dict[str, str]:
    """Return wallet address only."""
    return {"address": wallet_service.get_wallet_address()}
