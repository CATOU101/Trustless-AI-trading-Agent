"""Trading state API routes."""

from fastapi import APIRouter

from app.services.trading_service import trading_service

router = APIRouter(tags=["trading"])


@router.get("/portfolio")
async def get_portfolio() -> dict[str, object]:
    """Return current in-memory portfolio state."""
    return trading_service.get_portfolio()


@router.get("/trades")
async def get_trade_history() -> list[dict[str, object]]:
    """Return in-memory trade history."""
    return trading_service.get_trade_history()
