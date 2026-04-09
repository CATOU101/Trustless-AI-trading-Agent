# AutoHedge AI

AutoHedge AI is a full-stack autonomous crypto trading demo built around a FastAPI backend and a React + Tailwind dashboard.

It combines:
- live crypto market data
- deterministic multi-agent trading decisions
- Ollama-generated explanations
- risk controls
- paper trading
- persistent agent identity
- auditable trade artifacts
- Sepolia ERC-8004 shared contract integration
- autonomous backend scanning
- live dashboard monitoring

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
- identity and artifact visibility
- current-asset trade intent visibility
- autonomous runner status

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

The project includes an ERC-8004-style agent identity layer, Sepolia shared contract integration, and an auditable artifact trail.

Identity:
- [backend/app/services/identity_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/identity_service.py)
- persisted at [backend/app/agent_identity.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/agent_identity.json)

Wallet:
- [backend/app/services/wallet_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/wallet_service.py)
- persisted at [backend/app/agent_wallet.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/agent_wallet.json)

Trade intent signing:
- [backend/app/services/intent_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/intent_service.py)

Sepolia shared contract integration:
- [backend/app/services/erc8004_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/erc8004_service.py)

Artifacts:
- [backend/app/services/artifact_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/artifact_service.py)
- persisted at [backend/app/artifacts.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/artifacts.json)

Artifacts currently cover:
- strategy decisions
- risk checks
- trade intents
- execution results

Onchain sync currently mirrors:
- agent registration to `AgentRegistry`
- sandbox allocation claim through `HackathonVault`
- signed trade intent submission to `RiskRouter`
- artifact hash checkpointing to `ValidationRegistry`

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

## Dashboard Highlights

- Market source visibility: Kraken REST and live source indicator
- Identity panel: agent name, wallet, agent ID, registry type, chain ID, capabilities
- Intent panel: current-asset trade intent artifact with action, amount, signature summary, and chain metadata
- Artifact panel: recent validation artifacts with status and hash
- Autonomous runner panel: running status, scan interval, and execution mode visibility

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
python -m venv .venv
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

The backend can use a local Ollama model for explanation text.

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

## Sepolia ERC-8004 Integration

The backend now includes a thin onchain integration layer for the shared ERC-8004 hackathon contracts on Sepolia.

Chain:
- `11155111` (`Sepolia`)

Contracts:
- `AgentRegistry`: `0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3`
- `HackathonVault`: `0x0E7CD8ef9743FEcf94f9103033a044caBD45fC90`
- `RiskRouter`: `0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC`
- `ReputationRegistry`: `0x423a9904e39537a9997fbaF0f220d79D7d545763`
- `ValidationRegistry`: `0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1`

The integration layer is best-effort and non-fatal:
- if RPC configuration is missing, the backend continues in local-only mode
- if contract calls fail, the trading workflow continues and logs a warning

Environment variables used by the backend:

```env
SEPOLIA_RPC_URL=https://your-sepolia-rpc
AGENT_PRIVATE_KEY=0xyour_private_key
```

Behavior:
- on startup, the backend attempts to register the agent onchain
- if registration succeeds, the returned onchain id is stored as `registry_agent_id`
- if available, the backend claims the sandbox allocation once
- after signed intent creation, the backend submits the intent to `RiskRouter`
- after artifact creation, the backend posts the artifact hash to `ValidationRegistry`

Important note:
- the contract ABIs in the service are placeholder fragments intended for wiring and integration
- replace them with verified shared contract ABIs for production-grade Sepolia usage

## Additional Documentation

- Backend details: [backend/README.md](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/README.md)
- Frontend details: [frontend/README.md](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/README.md)
