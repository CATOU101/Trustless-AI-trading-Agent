# Explainable AI Trading Agent Backend

Initial backend foundation for an explainable cryptocurrency trading agent built with FastAPI.

## Features

- Async FastAPI API design
- Modular architecture (`routes`, `services`, `models`, `core`, `utils`)
- Placeholder market and agent services for quick iteration
- Explainable trading output (`BUY` / `SELL` / `HOLD`)

## Project Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── market.py
│   │   └── agent.py
│   ├── services/
│   │   ├── market_service.py
│   │   └── agent_service.py
│   ├── models/
│   │   └── decision.py
│   ├── utils/
│   │   └── logger.py
│   └── core/
│       └── settings.py
├── requirements.txt
└── README.md
```

## Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Run the Server

```bash
cd backend
uvicorn app.main:app --reload
```

Server starts at `http://127.0.0.1:8000`.

## Ollama Requirement

The AI decision endpoint uses a local Ollama model (`llama3`) at `http://localhost:11434`.

Start Ollama before calling `/agent/analyze`:

```bash
ollama serve
ollama pull llama3
```

## API Endpoints

- `GET /health`
- `GET /market/price/{coin}`
- `GET /agent/profile`
- `POST /agent/analyze`

## Market Endpoint (CoinGecko)

`GET /market/price/{coin}` fetches live market data from the CoinGecko public API using the coin id (for example, `bitcoin`, `ethereum`, `solana`).

Response fields:

- `asset`: coin id
- `price_usd`: current USD price
- `change_24h`: 24-hour USD percentage change
- `market_cap`: current USD market capitalization

Example:

```http
GET /market/price/bitcoin
```

```json
{
  "asset": "bitcoin",
  "price_usd": 63000,
  "change_24h": -2.5,
  "market_cap": 1200000000000
}
```

If the coin id is invalid, the API returns `404`.

### Example Analyze Request

```json
{
  "coin": "bitcoin"
}
```

### Example Analyze Response

```json
{
  "asset": "bitcoin",
  "decision": "BUY",
  "confidence": 0.71,
  "reasoning": "Price dipped with moderate volatility suggesting a possible rebound.",
  "portfolio": {
    "cash_balance": 9000,
    "bitcoin": 0.015,
    "portfolio_value": 10020
  },
  "indicators": {
    "rsi": 28,
    "ma20": 62000
  }
}
```
