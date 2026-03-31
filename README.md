# AutoHedge AI

Full-stack autonomous AI trading agent with a FastAPI backend and React + Tailwind dashboard.

## Project Structure

```text
Trustless-AI-trading-Agent/
|- backend/
|  |- app/
|  |- requirements.txt
|  `- README.md
|- frontend/
|  |- src/
|  |- package.json
|  `- README.md
`- README.md
```

## What It Includes

- FastAPI backend for market data, multi-agent decisioning, paper trading, and backtesting
- Kraken integration (CLI execution with sandbox fallback, REST market pricing)
- ERC-8004-style agent identity endpoint and audit artifacts
- EIP-712 signed trade intents with verification
- React dashboard with autonomous runner visibility, identity, intent, artifacts, portfolio, votes, indicators, leaderboard, and trade history

## API Endpoints

- `GET /agent/decision`
- `GET /agent/identity`
- `GET /agent/artifacts`
- `GET /agents/decisions`
- `GET /agents/leaderboard`
- `GET /portfolio`
- `GET /trades`
- `GET /market/price/{coin}`
- `GET /wallet`
- `GET /health`

## Dashboard Highlights

- Market source visibility: `Kraken REST` and live source indicator
- Identity panel: agent name, wallet, agent ID, registry type (`ERC-8004`), chain ID, capabilities
- Intent panel: latest `trade_intent` artifact with asset, action, amount, truncated signature, and `domain.chainId`
- Artifact viewer: latest 5 validation artifacts with status and hash
- Autonomous runner panel: running status, 60s scan interval, mode, execution path (`Kraken CLI / Sandbox fallback`)

## Run Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000`.

## Run Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs at `http://localhost:3000`.

## Ollama

The backend can use a local Ollama model for explanation text.

```bash
ollama serve
ollama pull llama3
```

## More Details

- Backend documentation: [backend/README.md](backend/README.md)
- Frontend documentation: [frontend/README.md](frontend/README.md)
