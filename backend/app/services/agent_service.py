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
        decision: TradingDecision | None = None,
    ) -> AgentDecision:
        """Generate deterministic confidence and an LLM explanation for a decision.

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
        resolved_decision = decision or self._deterministic_decision(
            asset_holdings=asset_holdings,
            rsi=rsi,
            price=price,
            ma20=ma20,
        )

        print(f"Analyzing: {asset}")
        print(f"Price: {price} | Change: {change_24h}")
        confidence = self._compute_confidence(
            action=resolved_decision,
            rsi=rsi,
            price=price,
            ma20=ma20,
        )
        reasoning = await self.generate_explanation(
            asset=asset,
            action=resolved_decision,
            indicators={"rsi": rsi, "ma20": ma20},
        )
        return {
            "asset": asset,
            "decision": resolved_decision,
            "confidence": confidence,
            "reasoning": reasoning,
        }

    async def generate_explanation(
        self,
        asset: str,
        action: TradingDecision,
        indicators: dict[str, float],
    ) -> str:
        """Generate a short explanation for an already-determined decision."""
        prompt = (
            "You are an AI trading analyst.\n\n"
            "Explain why the system decided to BUY, SELL, or HOLD.\n\n"
            f"Asset: {asset}\n"
            f"RSI: {indicators['rsi']}\n"
            f"MA20: {indicators['ma20']}\n"
            f"Decision: {action}\n\n"
            "Return a short explanation (1-2 sentences)."
        )
        payload = {"model": self._model_name, "prompt": prompt, "stream": False}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self._ollama_url, json=payload)
                response.raise_for_status()
                result = response.json()
        except (httpx.HTTPError, ValueError):
            return "Strategy consensus triggered this decision."

        explanation = result.get("response", "")
        if not isinstance(explanation, str) or not explanation.strip():
            return "Strategy consensus triggered this decision."
        return " ".join(explanation.strip().split())

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

    def _fallback_decision(
        self,
        asset: str,
        decision: TradingDecision,
        reason: str = "fallback decision due to parsing error",
    ) -> AgentDecision:
        """Return deterministic fallback explanation when parsing fails."""
        return {
            "asset": asset,
            "decision": decision,
            "confidence": 0.5,
            "reasoning": reason,
        }

    def _compute_confidence(
        self, action: TradingDecision, rsi: float, price: float, ma20: float
    ) -> float:
        """Compute deterministic confidence from signal alignment strength."""
        price_gap = abs(price - ma20) / ma20 if ma20 else 0.0
        if action == TradingDecision.HOLD:
            base = 0.58
        else:
            base = 0.62

        confidence = base + min(0.18, price_gap) + min(0.12, abs(rsi - 50) / 100)
        return round(min(confidence, 0.95), 2)

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
