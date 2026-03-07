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
        decision = self._deterministic_decision(
            asset_holdings=asset_holdings,
            rsi=rsi,
            price=price,
            ma20=ma20,
        )

        print(f"Analyzing coin: {asset}")
        print(f"Price: {price} | Change: {change_24h}")

        prompt = (
            "You are an AI trading analyst explaining a trading decision.\n\n"
            "Market Data:\n"
            f"Asset: {asset}\n"
            f"Price: {price}\n"
            f"RSI: {rsi}\n"
            f"Moving Average: {ma20}\n\n"
            "Trading Decision:\n"
            f"{decision}\n\n"
            "Explain why this decision is reasonable.\n\n"
            "Return JSON:\n\n"
            "{\n"
            f'  "decision": "{decision}",\n'
            '  "confidence": 0.0-1.0,\n'
            '  "reasoning": "technical explanation"\n'
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
        except httpx.HTTPStatusError:
            return self._fallback_decision(asset, "fallback decision due to ollama api error")

        try:
            result = response.json()
        except ValueError:
            return self._fallback_decision(
                asset, "fallback decision due to malformed ollama response"
            )

        raw_text = result.get("response", "")
        if not isinstance(raw_text, str) or not raw_text.strip():
            return self._fallback_decision(asset, decision)

        parsed = self._parse_json_response(raw_text)
        explained = self._validate_explanation(
            asset=asset,
            expected_decision=decision,
            parsed=parsed,
        )
        if explained is None:
            return self._fallback_decision(asset, decision)
        return explained

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

    def _validate_explanation(
        self,
        asset: str,
        expected_decision: TradingDecision,
        parsed: dict[str, object] | None,
    ) -> AgentDecision | None:
        """Validate parsed model output and normalize into explanation payload."""
        if not parsed:
            return None

        reasoning = str(parsed.get("reasoning", "")).strip()

        try:
            confidence = float(parsed.get("confidence"))
        except (TypeError, ValueError):
            return None

        if not 0.0 <= confidence <= 1.0:
            return None
        if not reasoning:
            return None

        return {
            "asset": asset,
            "decision": expected_decision,
            "confidence": confidence,
            "reasoning": reasoning,
        }

    def _fallback_decision(self, asset: str, decision: TradingDecision) -> AgentDecision:
        """Return deterministic fallback explanation when parsing fails."""
        return {
            "asset": asset,
            "decision": decision,
            "confidence": 0.5,
            "reasoning": "fallback decision due to parsing error",
        }

    def _deterministic_decision(
        self, asset_holdings: float, rsi: float, price: float, ma20: float
    ) -> TradingDecision:
        """Compute deterministic trading action from indicators and exposure limits."""
        if rsi < 30:
            decision = TradingDecision.BUY
        elif rsi > 70:
            decision = TradingDecision.SELL
        elif price > ma20:
            decision = TradingDecision.HOLD
        else:
            decision = TradingDecision.HOLD

        if asset_holdings > 10:
            decision = TradingDecision.HOLD

        return decision


agent_service = AgentService()
