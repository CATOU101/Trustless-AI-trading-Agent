# Explainable AI Trading Agent Backend

FastAPI backend for an autonomous crypto trading demo with multi-agent strategy coordination, risk controls, paper trading, and simulated decentralized execution.

## Features

- Async FastAPI API design
- Modular architecture (`routes`, `services`, `models`, `core`, `utils`)
- CoinGecko market data integration
- Technical indicators (RSI, MA20)
- Multi-agent strategy voting and coordinator
- Risk management + reputation tracking
- Autonomous runner (scans assets every 60 seconds)
- Paper trading sandbox (starts with `$10,000`)
- Wallet identity (`agent_wallet.json`)
- Signed trade intents
- DEX quote + swap simulation (0x with deterministic fallback)

## Trade Flow

`Decision -> Intent Creation -> Intent Signature -> DEX Quote -> Simulated Swap -> Portfolio Update`

Note: no real blockchain transaction is broadcast in this demo.

## Project Structure

```text
backend/
|-- app/
|   |-- main.py
|   |-- config.py
|   |-- routes/
|   |   |-- market.py
|   |   |-- agent.py
|   |   |-- agents.py
|   |   |-- trading.py
|   |   |-- wallet.py
|   |   `-- backtest.py
|   |-- services/
|   |   |-- market_service.py
|   |   |-- indicator_service.py
|   |   |-- agent_coordinator.py
|   |   |-- risk_service.py
|   |   |-- reputation_service.py
|   |   |-- trading_service.py
|   |   |-- wallet_service.py
|   |   |-- intent_service.py
|   |   `-- dex_service.py
|   |-- models/
|   |   `-- decision.py
|   |-- utils/
|   |   |-- logger.py
|   |   `-- task_cleanup.py
|   `-- agent_wallet.json (auto-created)
|-- requirements.txt
`-- README.md
```

## Setup (Windows PowerShell)

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Setup (macOS/Linux)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run Server

```bash
python -m uvicorn app.main:app --reload
```

API base URL: `http://127.0.0.1:8000`

## Ollama Requirement

`POST /agent/analyze` uses local Ollama (`llama3`) for explanation text.

```bash
ollama serve
ollama pull llama3
```

If Ollama is unavailable, the backend falls back to deterministic explanation text.

## API Endpoints

- `GET /health`
- `GET /market/price/{coin}`
- `GET /agent/profile`
- `POST /agent/analyze`
- `GET /agents`
- `GET /agents/decisions?coin=bitcoin`
- `GET /agents/leaderboard`
- `GET /portfolio`
- `GET /trades`
- `GET /wallet`
- `GET /wallet/address`
- `GET /backtest/{coin}`

## Wallet + Intent Notes

- Wallet file is persisted at `backend/app/agent_wallet.json`.
- Trade records now include wallet metadata for traceability.
- Intent signature verification is enforced before simulated swap execution.

## Example Wallet Response

```json
{
  "address": "0xA123...",
  "balance": 10000
}
```
