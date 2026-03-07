"""Historical backtesting service for strategy evaluation."""

from typing import TypedDict

import httpx

from app.services.indicator_service import calculate_moving_average, calculate_rsi


class BacktestResult(TypedDict):
    """Backtesting summary and portfolio curve."""

    starting_balance: float
    ending_balance: float
    return_percent: float
    total_trades: int
    portfolio_curve: list[float]


class BacktestService:
    """Service to run historical simulations over CoinGecko data."""

    _market_chart_url: str = "https://api.coingecko.com/api/v3/coins/{coin}/market_chart"

    async def fetch_historical_prices(self, coin: str, days: int = 60) -> list[float]:
        """Fetch daily historical prices from CoinGecko."""
        normalized = coin.strip().lower()
        params = {"vs_currency": "usd", "days": days, "interval": "daily"}

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                self._market_chart_url.format(coin=normalized), params=params
            )
            response.raise_for_status()
            payload = response.json()

        points = payload.get("prices", [])
        prices = [float(point[1]) for point in points if len(point) >= 2]
        if len(prices) < 20:
            raise ValueError(f"Not enough historical prices for coin '{coin}'.")

        return prices

    async def run_backtest(self, coin: str) -> BacktestResult:
        """Run strategy simulation over historical prices."""
        prices = await self.fetch_historical_prices(coin=coin, days=60)

        starting_balance = 10000.0
        cash_balance = starting_balance
        asset_holdings = 0.0
        total_trades = 0
        portfolio_curve: list[float] = []

        for idx, price in enumerate(prices):
            history = prices[: idx + 1]

            try:
                rsi = calculate_rsi(history, period=14)
            except ValueError:
                rsi = 50.0

            try:
                ma20 = calculate_moving_average(history, period=20)
            except ValueError:
                ma20 = price

            if rsi < 35:
                decision = "BUY"
            elif rsi > 65:
                decision = "SELL"
            elif price < ma20 * 0.98:
                decision = "BUY"
            elif price > ma20 * 1.02:
                decision = "SELL"
            else:
                decision = "HOLD"

            if decision == "BUY" and cash_balance > 0:
                amount = (cash_balance * 0.1) / price
                asset_holdings += amount
                cash_balance -= amount * price
                total_trades += 1
            elif decision == "SELL" and asset_holdings > 0:
                amount = asset_holdings * 0.1
                asset_holdings -= amount
                cash_balance += amount * price
                total_trades += 1

            portfolio_value = cash_balance + asset_holdings * price
            portfolio_curve.append(round(portfolio_value, 6))

        ending_balance = portfolio_curve[-1] if portfolio_curve else starting_balance
        total_return = (ending_balance - starting_balance) / starting_balance

        return {
            "starting_balance": round(starting_balance, 2),
            "ending_balance": round(ending_balance, 2),
            "return_percent": round(total_return * 100, 2),
            "total_trades": total_trades,
            "portfolio_curve": portfolio_curve,
        }


backtest_service = BacktestService()
