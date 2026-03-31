# AutoHedge AI Backend

The AutoHedge AI backend is a FastAPI service for an autonomous multi-agent crypto trading demo.

It handles:
- market data retrieval
- indicator calculation
- multi-agent vote coordination
- autonomous scanning
- risk checks
- paper trading
- identity persistence
- artifact logging
- leaderboard tracking
- backtesting

## Backend Responsibilities

The backend runs the full trading workflow:
1. fetch market data
2. compute RSI and MA20
3. collect votes from strategy agents
4. aggregate a final decision
5. apply risk controls
6. enforce position-aware trading rules
7. generate explanation text with Ollama
8. execute a sandbox trade or optional Kraken CLI path
9. log audit artifacts
10. update reputation and trade history

## Stack

- Python
- FastAPI
- Pydantic
- httpx
- Ollama
- Kraken REST
- CoinGecko fallback

## Main Modules

### Core App
- [app/main.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/main.py)
- [app/config.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/config.py)
- [app/core/settings.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/core/settings.py)

### Routes
- [app/routes/market.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/routes/market.py)
- [app/routes/agent.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/routes/agent.py)
- [app/routes/agents.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/routes/agents.py)
- [app/routes/trading.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/routes/trading.py)
- [app/routes/backtest.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/routes/backtest.py)
- [app/routes/identity.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/routes/identity.py)
- [app/routes/artifacts.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/routes/artifacts.py)
- [app/routes/wallet.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/routes/wallet.py)

### Services
- [app/services/market_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/market_service.py)
- [app/services/kraken_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/kraken_service.py)
- [app/services/indicator_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/indicator_service.py)
- [app/services/agent_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agent_service.py)
- [app/services/agent_coordinator.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agent_coordinator.py)
- [app/services/agent_runner.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agent_runner.py)
- [app/services/risk_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/risk_service.py)
- [app/services/trading_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/trading_service.py)
- [app/services/reputation_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/reputation_service.py)
- [app/services/backtest_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/backtest_service.py)
- [app/services/wallet_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/wallet_service.py)
- [app/services/intent_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/intent_service.py)
- [app/services/dex_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/dex_service.py)
- [app/services/identity_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/identity_service.py)
- [app/services/artifact_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/artifact_service.py)

### Strategy Agents
- [app/services/agents/momentum_agent.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agents/momentum_agent.py)
- [app/services/agents/mean_reversion_agent.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agents/mean_reversion_agent.py)
- [app/services/agents/trend_agent.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agents/trend_agent.py)

## Autonomous Behavior

The backend launches the autonomous runner on startup.

Currently scanned assets:
- `bitcoin`
- `ethereum`
- `solana`

The runner loops every 60 seconds and does not require any frontend trigger.

## Market Data

Market data priority:
1. Kraken REST
2. CoinGecko fallback

The service returns normalized market payloads with:
- `asset`
- `price`
- `price_usd`
- `change_24h`
- `market_cap`
- `prices`

Historical prices are used for:
- RSI
- MA20
- backtesting

## Decision System

### Strategy Agents

The backend uses three deterministic agents:

`MomentumAgent`
- BUY if `RSI < 40` and `price > MA20`
- SELL if `RSI > 70`
- else HOLD

`MeanReversionAgent`
- BUY if `RSI < 30`
- SELL if `RSI > 70`
- else HOLD

`TrendAgent`
- BUY if `price > MA20`
- SELL if `price < MA20`
- else HOLD

### Vote Aggregation

Votes are encoded as:
- `BUY = +1`
- `SELL = -1`
- `HOLD = 0`

Final action rules:
- score `> 0` => `BUY`
- score `< 0` => `SELL`
- score `== 0` => `HOLD`

Final confidence is the average of agent confidences.

### Explanation Layer

Ollama is used only for explanation text.

It does not decide the trade action. The backend computes the final action first, then Ollama explains it.

If Ollama is unavailable, the backend falls back gracefully.

## Risk and Trading

### Risk Controls

Risk layer includes:
- drawdown protection
- volatility-based position sizing
- repeated-trade cooldown

### Position-Aware Guard

The backend will override impossible trades:
- `SELL` with zero holdings => `HOLD`
- `BUY` with zero cash => `HOLD`

### Trading Mode

Execution priority:
1. Kraken CLI if available and compatible
2. sandbox trading fallback

This means the backend can continue working even when live execution tooling is unavailable.

The sandbox starts with:
- `cash_balance = 10000`

## Identity, Intent, and Audit Trail

### Identity

The backend persists an ERC-8004-style agent identity in:
- [app/agent_identity.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/agent_identity.json)

Identity fields include:
- `agent_name`
- `wallet`
- `version`
- `registry_type`
- `chain_id`
- `agent_id`
- `capabilities`
- `endpoints`
- `artifact_endpoint`

### Wallet

Wallet is persisted in:
- [app/agent_wallet.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/agent_wallet.json)

### Trade Intent Signing

Trade intents are signed with an EIP-712-style typed payload in:
- [app/services/intent_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/intent_service.py)

### Artifacts

Artifacts are persisted in:
- [app/artifacts.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/artifacts.json)

Artifact types include:
- strategy decision
- risk check
- trade intent
- execution result

Artifacts also include:
- `validation_status`
- `artifact_hash`

## API Endpoints

### Health
- `GET /health`

### Market
- `GET /market/price/{coin}`

### Agent
- `POST /agent/analyze`
- `GET /agent/decision`
- `GET /agent/profile`
- `GET /agent/identity`
- `GET /agent/artifacts`

### Multi-Agent
- `GET /agents`
- `GET /agents/decisions`
- `GET /agents/leaderboard`

### Trading
- `GET /portfolio`
- `GET /trades`

### Wallet
- `GET /wallet`
- `GET /wallet/address`

### Backtesting
- `GET /backtest/{coin}`

## Project Structure

```text
backend/
├── app/
│   ├── core/
│   ├── models/
│   ├── routes/
│   ├── services/
│   │   └── agents/
│   ├── utils/
│   ├── agent_identity.json
│   ├── agent_wallet.json
│   └── artifacts.json
├── requirements.txt
└── README.md
```

## Setup

### macOS / Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

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

## Run The Backend

```bash
python -m uvicorn app.main:app --reload
```

Base URL:
- `http://127.0.0.1:8000`

## Ollama Setup

The backend expects a local Ollama server for explanations.

```bash
ollama serve
ollama pull llama3
```

Expected endpoint:
- `http://localhost:11434`

## Kraken Notes

The backend uses:
- Kraken REST for primary market data
- a dedicated Kraken CLI path for optional execution
- sandbox fallback for resilience

Current configured CLI path:
- `/Users/madhavan/kraken-cli-env/bin/kraken`

This layered setup lets the system keep running even when execution tooling is unavailable or partially configured.
