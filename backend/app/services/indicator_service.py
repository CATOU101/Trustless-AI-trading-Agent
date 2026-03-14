"""Technical indicator calculations for market analysis."""

from typing import TypedDict


class IndicatorData(TypedDict):
    """Calculated technical indicators."""

    rsi: float
    ma20: float


def calculate_rsi(prices: list[float], period: int = 14) -> float:
    """Calculate RSI from a series of prices.

    Uses:
    RSI = 100 - (100 / (1 + RS))
    where RS = average_gain / average_loss
    """
    if period <= 0:
        raise ValueError("RSI period must be greater than zero.")
    if len(prices) < period + 1:
        raise ValueError("Not enough price points to calculate RSI.")

    deltas = [prices[idx] - prices[idx - 1] for idx in range(1, len(prices))]
    recent_deltas = deltas[-period:]
    gains = [delta for delta in recent_deltas if delta > 0]
    losses = [-delta for delta in recent_deltas if delta < 0]

    average_gain = sum(gains) / period
    average_loss = sum(losses) / period

    if average_loss == 0:
        return 100.0

    rs = average_gain / average_loss
    return round(100 - (100 / (1 + rs)), 4)


def moving_average(prices: list[float], window: int = 20) -> float:
    """Calculate simple moving average over the specified window."""
    if window <= 0:
        raise ValueError("Moving average period must be greater than zero.")
    if len(prices) < window:
        raise ValueError("Not enough price data")

    recent_prices = prices[-window:]
    return round(sum(recent_prices) / window, 4)


def calculate_moving_average(prices: list[float], period: int = 20) -> float:
    """Backward-compatible wrapper for moving average calculation."""
    return moving_average(prices=prices, window=period)


def compute_indicators(prices: list[float]) -> IndicatorData:
    """Compute RSI and MA20 from historical prices."""
    return {
        "rsi": calculate_rsi(prices=prices, period=14),
        "ma20": moving_average(prices=prices, window=20),
    }
