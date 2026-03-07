"""Agent service for generating explainable trading decisions via Ollama."""

import json
import re
from typing import TypedDict

import httpx

from app.models.decision import TradingDecision


class OllamaUnavailableError(Exception):
    """Raised when the local Ollama service is unavailable."""


class AgentDecision(TypedDict):
    """Typed payload for model decision output."""

    asset: str
    decision: TradingDecision
    confidence: float
    reasoning: str


class AgentService:
    """Service layer for AI-based decision generation."""

    _ollama_url: str = "http://localhost:11434/api/generate"
    _model_name: str = "llama3"

    async def analyze_market(
        self,
        asset: str,
        price: float,
        change_24h: float,
        rsi: float,
        ma20: float,
        cash_balance: float,
        asset_holdings: float,
    ) -> AgentDecision:
        """Generate an explainable decision using a local Ollama model.

        Args:
            asset: CoinGecko asset id.
            price: Current USD price.
            change_24h: 24-hour percentage price change.
            rsi: Relative Strength Index value.
            ma20: 20-day moving average.
            cash_balance: Current portfolio cash balance.
            asset_holdings: Quantity held for the analyzed asset.

        Returns:
            Parsed AI decision payload.

        Raises:
            OllamaUnavailableError: If Ollama is unreachable.
            httpx.HTTPError: If Ollama returns an error status.
        """
        prompt = (
            "You are an AI quantitative crypto trading analyst working in a simulated "
            "trading environment.\n\n"
            "Your job is to analyze market data and recommend a trading action.\n\n"
            "You are NOT giving financial advice.\n"
            "You are executing an automated trading strategy.\n\n"
            "Market Data:\n"
            f"Asset: {asset}\n"
            f"Price: {price}\n"
            f"24h Change: {change_24h} %\n\n"
            "Market Indicators:\n"
            f"RSI: {rsi}\n"
            f"20-day Moving Average: {ma20}\n\n"
            "Portfolio State:\n"
            f"Cash Balance: {cash_balance}\n"
            f"Asset Holdings: {asset_holdings}\n\n"
            "Trading Strategy Rules:\n"
            "1. If price dropped more than 4% in 24h -> BUY (dip buying opportunity)\n"
            "2. If price increased more than 4% -> SELL (profit taking)\n"
            "3. If price change is between -4% and +4% -> HOLD\n"
            "4. If portfolio already holds a large position -> avoid BUY\n"
            "5. If market signals are unclear -> HOLD\n\n"
            "Indicator Rules:\n"
            "1. If RSI < 30, market is oversold -> consider BUY\n"
            "2. If RSI > 70, market is overbought -> consider SELL\n"
            "3. If price > moving average, trend is bullish\n"
            "4. If price < moving average, trend is bearish\n\n"
            "Return ONLY valid JSON in this format:\n\n"
            "{\n"
            '  "decision": "BUY | SELL | HOLD",\n'
            '  "confidence": 0.0-1.0,\n'
            '  "reasoning": "short explanation referencing price movement and '
            'portfolio risk"\n'
            "}\n"
        )

        payload = {"model": self._model_name, "prompt": prompt, "stream": False}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self._ollama_url, json=payload)
                response.raise_for_status()
        except httpx.ConnectError as exc:
            raise OllamaUnavailableError(
                "Ollama is not reachable at http://localhost:11434. "
                "Ensure the Ollama server is running."
            ) from exc

        result = response.json()
        raw_text = result.get("response", "")
        parsed = self._parse_json_response(raw_text)
        decision = self._validate_decision(asset=asset, parsed=parsed)
        if decision is None:
            return self._fallback_decision(asset)
        return decision

    def _parse_json_response(self, raw_text: str) -> dict[str, object] | None:
        """Extract and parse JSON object from model text output."""
        content = raw_text.strip()
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, flags=re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    return None
            return None

    def _validate_decision(
        self, asset: str, parsed: dict[str, object] | None
    ) -> AgentDecision | None:
        """Validate parsed model output and normalize into decision payload."""
        if not parsed:
            return None

        decision_raw = str(parsed.get("decision", "")).upper().strip()
        reasoning = str(parsed.get("reasoning", "")).strip()

        try:
            confidence = float(parsed.get("confidence"))
        except (TypeError, ValueError):
            return None

        if decision_raw not in TradingDecision.__members__:
            return None
        if not 0.0 <= confidence <= 1.0:
            return None
        if not reasoning:
            return None

        return {
            "asset": asset,
            "decision": TradingDecision[decision_raw],
            "confidence": confidence,
            "reasoning": reasoning,
        }

    def _fallback_decision(self, asset: str) -> AgentDecision:
        """Return deterministic fallback decision when parsing/validation fails."""
        return {
            "asset": asset,
            "decision": TradingDecision.HOLD,
            "confidence": 0.5,
            "reasoning": "fallback decision due to parsing error",
        }


agent_service = AgentService()
