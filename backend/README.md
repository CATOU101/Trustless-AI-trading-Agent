# AutoHedge AI Backend

## Overview
The AutoHedge AI backend is a FastAPI service that powers the autonomous trading workflow.

It is responsible for:
- pulling market data
- computing indicators
- coordinating deterministic strategy agents
- applying risk and position-aware safeguards
- generating optional LLM explanations
- signing EIP-712 trade intents
- logging artifacts
- mirroring validation data to Sepolia ERC-8004 contracts

The backend is designed so that local trading logic continues to work even if Ollama, Kraken CLI, or Sepolia writes are unavailable.

## Key Responsibilities
1. fetch market data
2. compute RSI and MA20
3. collect strategy votes
4. aggregate a final action
5. apply risk controls
6. enforce position-aware rules
7. generate explanation text
8. create and sign trade intents
9. execute through Kraken CLI or sandbox fallback
10. persist artifacts and identity state
11. mirror relevant checkpoints onchain

## Architecture
```text
Kraken REST / CoinGecko
          ↓
     Indicators
          ↓
  Strategy Agents
          ↓
     Aggregator
          ↓
      Risk Layer
          ↓
   Trade Intent + Signing
          ↓
  Execution / Sandbox Path
          ↓
 Artifact Logging + ERC-8004
```

## Stack
- Python
- FastAPI
- Pydantic
- httpx
- Web3.py
- Kraken REST
- Ollama (optional)

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
- [app/services/erc8004_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/erc8004_service.py)

## Autonomous Behavior
The backend launches the autonomous runner on startup.

Current scan target:
- `ethereum`

Run interval:
- every 60 seconds

The runner does not need a frontend trigger.

## Market Data
Market data priority:
1. Kraken REST
2. CoinGecko fallback

Returned market payloads include:
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

The backend computes the decision first, then generates an explanation.

If Ollama is unavailable, or if `USE_LLM=false`, the backend falls back to:
- `Decision generated by multi-agent strategy using RSI and MA20 indicators.`

## Risk and Trading

### Risk Controls
The backend includes:
- drawdown protection
- repeated-trade cooldown
- volatility-based position sizing

### Position-Aware Guard
Impossible trades are overridden:
- `SELL` with zero holdings => `HOLD`
- `BUY` with zero cash => `HOLD`

### Execution Mode
Execution priority:
1. Kraken CLI if compatible and available
2. sandbox trading fallback

This allows the system to keep running even when live execution tooling is unavailable.

## Identity, Intent, and Artifacts

### Identity
The backend persists an ERC-8004-style identity in:
- [app/agent_identity.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/agent_identity.json)

Identity fields include:
- `agent_name`
- `wallet`
- `version`
- `registry_type`
- `chain_id`
- `agent_id`
- `registry_agent_id`
- `allocation_claimed`
- `capabilities`
- `endpoints`
- `artifact_endpoint`

### Wallet
Wallet is persisted in:
- [app/agent_wallet.json](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/agent_wallet.json)

### Trade Intents
Trade intents are signed with an EIP-712-style typed payload in:
- [app/services/intent_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/intent_service.py)

After signing, the backend attempts to submit intents to `RiskRouter`.

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

After persistence, artifact hashes can be mirrored to `ValidationRegistry`.

## ERC-8004 Integration

Chain ID:
- `11155111`

Contracts:
- `AgentRegistry`: `0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3`
- `HackathonVault`: `0x0E7CD8ef9743FEcf94f9103033a044caBD45fC90`
- `RiskRouter`: `0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC`
- `ReputationRegistry`: `0x423a9904e39537a9997fbaF0f220d79D7d545763`
- `ValidationRegistry`: `0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1`

Contract integration file:
- [app/services/erc8004_service.py](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/backend/app/services/erc8004_service.py)

Current onchain behavior:
- reuse local identity to avoid repeated registration
- claim sandbox allocation once when applicable
- submit signed intents to `RiskRouter`
- submit validation hashes to `ValidationRegistry`

This integration is best-effort:
- missing RPC config does not block local execution
- contract call failures log warnings and preserve local flow

## API Endpoints
- `GET /health`
- `GET /market/price/{coin}`
- `POST /agent/analyze`
- `GET /agent/decision`
- `GET /agent/profile`
- `GET /agent/identity`
- `GET /agent/artifacts`
- `GET /agents`
- `GET /agents/decisions`
- `GET /agents/leaderboard`
- `GET /portfolio`
- `GET /trades`
- `GET /backtest/{coin}`
- `GET /wallet`
- `GET /wallet/address`

## Running Locally
```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Optional environment variables:
```env
SEPOLIA_RPC_URL=https://your-sepolia-rpc
AGENT_PRIVATE_KEY=0xyour_private_key
USE_LLM=false
```
