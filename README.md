# AutoHedge AI

AutoHedge AI is an autonomous multi-agent crypto trading platform built for hackathon-style demos.

It combines:
- live crypto market data
- deterministic multi-agent trading decisions
- Ollama-generated explanations
- risk controls
- paper trading
- persistent agent identity
- auditable trade artifacts
- a React dashboard for live monitoring

## What The System Does

The backend runs an autonomous agent loop that scans supported assets on a schedule, computes indicators, gathers votes from multiple trading agents, applies risk and position checks, optionally executes a simulated trade, and records audit artifacts.

The frontend is a read-only dashboard that shows:
- latest decision
- confidence
- reasoning
- RSI and MA20
- portfolio state
- trade history
- agent votes
- leaderboard

## Architecture

### Backend

FastAPI backend with:
- market data services
- indicator calculations
- multi-agent coordination
- autonomous background runner
- sandbox trading
- reputation tracking
- identity and artifact persistence

Primary backend entrypoint:
- [backend/app/main.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/main.py)

### Frontend

React + Tailwind dashboard with polling every 60 seconds.

Frontend entrypoint:
- [frontend/src/App.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/App.js)

## Core Features

### Autonomous Agent Runner

The backend starts a background loop on startup and scans:
- `bitcoin`
- `ethereum`
- `solana`

Runner file:
- [backend/app/services/agent_runner.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agent_runner.py)

### Multi-Agent Strategy Layer

The system includes three deterministic strategy agents:
- `MomentumAgent`
- `MeanReversionAgent`
- `TrendAgent`

Agent implementations:
- [backend/app/services/agents/momentum_agent.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agents/momentum_agent.py)
- [backend/app/services/agents/mean_reversion_agent.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agents/mean_reversion_agent.py)
- [backend/app/services/agents/trend_agent.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agents/trend_agent.py)

Vote aggregation is handled by:
- [backend/app/services/agent_coordinator.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agent_coordinator.py)

Voting rules:
- `BUY = +1`
- `SELL = -1`
- `HOLD = 0`
- score `> 0` => `BUY`
- score `< 0` => `SELL`
- score `== 0` => `HOLD`

### Technical Indicators

Indicators currently used:
- RSI
- 20-day moving average (`MA20`)

Indicator service:
- [backend/app/services/indicator_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/indicator_service.py)

### Risk and Position Controls

Risk checks include:
- drawdown protection
- trade cooldown protection
- volatility-based position sizing

Position-aware safety checks include:
- no `SELL` when holdings are zero
- no `BUY` when cash is zero

Files:
- [backend/app/services/risk_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/risk_service.py)
- [backend/app/services/trading_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/trading_service.py)

### AI Explanations

Ollama is used only to explain the final decision.

It does not decide whether to buy or sell. The trade action is computed by backend logic first, then Ollama generates a short explanation.

Explanation service:
- [backend/app/services/agent_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agent_service.py)

### Identity, Wallet, Intent, and Artifacts

The project includes an ERC-8004-style agent identity layer and an auditable artifact trail.

Identity:
- [backend/app/services/identity_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/identity_service.py)
- persisted at [backend/app/agent_identity.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/agent_identity.json)

Wallet:
- [backend/app/services/wallet_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/wallet_service.py)
- persisted at [backend/app/agent_wallet.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/agent_wallet.json)

Trade intent signing:
- [backend/app/services/intent_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/intent_service.py)

Artifacts:
- [backend/app/services/artifact_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/artifact_service.py)
- persisted at [backend/app/artifacts.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/artifacts.json)

Artifacts currently cover:
- strategy decisions
- risk checks
- trade intents
- execution results

### Backtesting

Historical backtesting is supported through:
- [backend/app/services/backtest_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/backtest_service.py)

## Market Data and Execution

### Market Data Priority

The current market data flow is:
1. Kraken REST
2. CoinGecko fallback

Relevant files:
- [backend/app/services/kraken_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/kraken_service.py)
- [backend/app/services/market_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/market_service.py)

### Execution Priority

The current execution flow is:
1. Kraken CLI if compatible and available
2. sandbox execution fallback

Important note:
- the backend is wired to an explicit Kraken CLI path
- the project still keeps sandbox execution as the safe fallback path
- this means the app can continue functioning even when Kraken CLI execution is unavailable or unstable

## API Overview

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

### Backtesting
- `GET /backtest/{coin}`

### Wallet
- `GET /wallet`
- `GET /wallet/address`

## Project Structure

```text
AI Trading agent/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   │   └── agents/
│   │   └── utils/
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   └── services/
│   ├── package.json
│   └── README.md
└── README.md
```

## Running The Project

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend default URL:
- `http://127.0.0.1:8000`

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend default URL:
- `http://localhost:3000`

## Ollama Setup

Ollama is required for explanation text.

Example setup:

```bash
ollama serve
ollama pull llama3
```

The backend expects Ollama at:
- `http://localhost:11434`

## Kraken Notes

The backend is wired to use a dedicated Kraken CLI path:
- `/Users/madhavan/kraken-cli-env/bin/kraken`

Kraken integration is intentionally layered:
- Kraken REST is the primary market source
- Kraken CLI is an optional execution path
- sandbox execution remains available as fallback

This keeps the system demo-friendly and resilient even when external execution tooling is not fully available.

## Additional Documentation

- Backend details: [backend/README.md](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/README.md)
- Frontend details: [frontend/README.md](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/README.md)
