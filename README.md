# AutoHedge AI

## Overview
AutoHedge AI is an autonomous AI trading agent built with a FastAPI backend and a React + Tailwind dashboard.

The project combines:
- autonomous multi-agent market analysis
- ERC-8004-style on-chain agent identity
- EIP-712 signed trade intents
- validation checkpoints mirrored to Sepolia
- risk-aware execution with deterministic HOLD safeguards
- optional LLM-generated explanations

The backend runs on a schedule, evaluates market conditions, produces a decision, signs an intent, records artifacts, and exposes the full state through a live dashboard.

## Key Features
- Autonomous multi-agent decision system
- ERC-8004 identity registration
- ValidationRegistry checkpoints
- RiskRouter trade submission
- EIP-712 signed trade intents
- React dashboard
- Risk-aware HOLD logic

## Architecture
```text
Market Data
    ↓
Indicators
    ↓
Strategy Agents
    ↓
Aggregator
    ↓
Risk Layer
    ↓
Trade Intent
    ↓
ERC-8004 Validation
    ↓
Dashboard
```

### Backend
- FastAPI API and autonomous runner
- Kraken REST as primary market source
- CoinGecko fallback
- deterministic strategy evaluation
- EIP-712 signing
- ERC-8004 shared contract sync

Primary backend entrypoint:
- [backend/app/main.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/main.py)

### Frontend
- React + Tailwind dashboard
- polling-based read-only monitoring UI
- identity, intent, artifact, decision, portfolio, and leaderboard visibility

Frontend entrypoint:
- [frontend/src/App.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/App.js)

## Demo
- the autonomous agent runs every 60 seconds
- the runner currently scans `ethereum`
- HOLD decisions are expected behavior when votes are mixed or risk rules block action
- the EIP-712 panel shows the latest signed intent for the current asset
- on-chain validation checkpoints are logged when artifact submission is enabled

What you should expect during a demo:
- the system fetches market data
- RSI and MA20 are computed
- the three strategy agents vote independently
- the final action is aggregated and checked by the risk layer
- a signed trade intent is created even when the action is `HOLD`
- artifacts are persisted and optionally mirrored onchain

## Tech Stack
- FastAPI
- React + Tailwind
- Web3.py
- ERC-8004
- Kraken REST
- Ollama (optional)

## Core Flow

### Autonomous Runner
The backend starts a background loop on startup and currently scans:
- `ethereum`

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

Current strategy thresholds:

`MomentumAgent`
- BUY if `RSI < 45`
- SELL if `RSI > 65`
- else HOLD

`MeanReversionAgent`
- BUY if `RSI < 40`
- SELL if `RSI > 60`
- else HOLD

`TrendAgent`
- BUY if `price > MA20 * 1.002`
- SELL if `price < MA20 * 0.998`
- else HOLD

Vote aggregation is handled by:
- [backend/app/services/agent_coordinator.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agent_coordinator.py)

Voting rules:
- `BUY = +1`
- `SELL = -1`
- `HOLD = 0`
- score `> 0` => `BUY`
- score `< 0` => `SELL`
- score `== 0` => `HOLD`

### Indicators
Indicators currently used:
- RSI
- 20-day moving average (`MA20`)

Indicator service:
- [backend/app/services/indicator_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/indicator_service.py)

### Risk and Execution Safety
Risk checks include:
- drawdown protection
- repeated-trade cooldown
- volatility-based position sizing

Position-aware safety checks include:
- no `SELL` when holdings are zero
- no `BUY` when cash is zero

Relevant files:
- [backend/app/services/risk_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/risk_service.py)
- [backend/app/services/trading_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/trading_service.py)

### Explanations
Ollama is used only for explanation text.

It does not decide whether to buy or sell. The trade action is computed first by backend logic, and then the explanation layer describes that decision.

If Ollama is unavailable, or if `USE_LLM=false`, the backend falls back to a deterministic explanation.

Explanation service:
- [backend/app/services/agent_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/agent_service.py)

## Running Locally

### Backend
```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend URL:
- `http://127.0.0.1:8000`

### Frontend
```bash
cd frontend
npm install
HOST=127.0.0.1 PORT=3000 npm start
```

Frontend URL:
- `http://127.0.0.1:3000`

### Optional Ollama
```bash
ollama serve
ollama pull llama3
```

Optional deployment toggle:
```env
USE_LLM=false
```

## Deployment

### Render
The simplest deployment path is:
1. push the repository to GitHub
2. connect the repo to Render
3. deploy the backend service from the `backend` directory
4. set environment variables in Render
5. set `USE_LLM=false` if Ollama is not available in the deployment environment

Recommended backend environment variables:
```env
SEPOLIA_RPC_URL=https://your-sepolia-rpc
AGENT_PRIVATE_KEY=0xyour_private_key
USE_LLM=false
```

This allows the backend to run without local Ollama while keeping deterministic explanations active.

## ERC-8004 Integration
The backend includes a thin Sepolia integration layer for the shared ERC-8004 contracts.

Shared contracts:
- `AgentRegistry`
- `HackathonVault`
- `RiskRouter`
- `ReputationRegistry`
- `ValidationRegistry`

Current on-chain behavior:
- load the persistent agent identity
- reuse local agent identity to avoid repeated registration attempts
- submit signed intents to `RiskRouter`
- submit artifact hashes to `ValidationRegistry`
- keep local execution working even when on-chain calls fail

Relevant services:
- [backend/app/services/identity_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/identity_service.py)
- [backend/app/services/intent_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/intent_service.py)
- [backend/app/services/artifact_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/artifact_service.py)
- [backend/app/services/erc8004_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/erc8004_service.py)
- [backend/app/services/reputation_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/reputation_service.py)

Persistent files:
- [backend/app/agent_identity.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/agent_identity.json)
- [backend/app/agent_wallet.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/agent_wallet.json)
- [backend/app/artifacts.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/artifacts.json)

## Market Data and Execution
Market data priority:
1. Kraken REST
2. CoinGecko fallback

Execution priority:
1. Kraken CLI when available and compatible
2. sandbox fallback

This keeps the project demo-friendly and resilient even when external execution tooling is unavailable.

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

## Additional Documentation
- Backend details: [backend/README.md](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/README.md)
- Frontend details: [frontend/README.md](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/README.md)
