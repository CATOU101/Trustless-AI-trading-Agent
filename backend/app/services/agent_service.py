"""Agent service for generating explainable trading decisions via Ollama."""

import json
import re
from typing import TypedDict

import httpx

from app.models.decision import TradingDecision


class OllamaUnavailableError(Exception):
    """Raised when the local Ollama service is unavailable."""


class InvalidModelResponseError(Exception):
    """Raised when Ollama returns malformed or incomplete decision output."""


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
        self, asset: str, price: float, change_24h: float
    ) -> AgentDecision:
        """Generate an explainable decision using a local Ollama model.

        Args:
            asset: CoinGecko asset id.
            price: Current USD price.
            change_24h: 24-hour percentage price change.

        Returns:
            Parsed AI decision payload.

        Raises:
            OllamaUnavailableError: If Ollama is unreachable.
            InvalidModelResponseError: If model output is malformed.
            httpx.HTTPError: If Ollama returns an error status.
        """
        prompt = (
            "You are an AI crypto trading analyst. Based on the following market data "
            "decide whether to BUY, SELL, or HOLD.\n\n"
            f"Asset: {asset}\n"
            f"Price: {price}\n"
            f"24h Change: {change_24h}\n\n"
            "Respond in JSON format:\n\n"
            "{\n"
            ' "decision": "BUY | SELL | HOLD",\n'
            ' "confidence": 0.0-1.0,\n'
            ' "reasoning": "short explanation"\n'
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

        decision_raw = str(parsed.get("decision", "")).upper().strip()
        reasoning = str(parsed.get("reasoning", "")).strip()

        try:
            confidence = float(parsed.get("confidence"))
        except (TypeError, ValueError) as exc:
            raise InvalidModelResponseError(
                "Model response did not include a numeric confidence value."
            ) from exc

        if decision_raw not in TradingDecision.__members__:
            raise InvalidModelResponseError(
                "Model response decision must be one of BUY, SELL, HOLD."
            )
        if not 0.0 <= confidence <= 1.0:
            raise InvalidModelResponseError(
                "Model response confidence must be between 0.0 and 1.0."
            )
        if not reasoning:
            raise InvalidModelResponseError(
                "Model response did not include reasoning text."
            )

        return {
            "asset": asset,
            "decision": TradingDecision[decision_raw],
            "confidence": confidence,
            "reasoning": reasoning,
        }

    def _parse_json_response(self, raw_text: str) -> dict[str, object]:
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
                except json.JSONDecodeError as exc:
                    raise InvalidModelResponseError(
                        "Unable to parse JSON object from model response."
                    ) from exc
            raise InvalidModelResponseError(
                "Model response was not valid JSON."
            )


agent_service = AgentService()
