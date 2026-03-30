# AutoHedge AI

Full-stack hackathon demo for an autonomous AI trading agent.

## Project Structure

```text
AI Trading agent/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   ├── package.json
│   └── README.md
└── README.md
```

## What It Includes

- FastAPI backend for market data, multi-agent decisioning, paper trading, and backtesting
- React dashboard for portfolio, decisions, indicators, trade history, and leaderboard
- CoinGecko market data integration
- Ollama-powered explanation generation
- Autonomous background agent loop for BTC, ETH, and SOL

## Run Backend

```bash
cd backend
python3 -m venv .venv
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

The backend uses a local Ollama model for explanation text.

```bash
ollama serve
ollama pull llama3
```

## More Details

- Backend documentation: [backend/README.md](/Users/madhavan/Documents/CODE/AI%20Trading%20agent/backend/README.md)
- Frontend documentation: [frontend/README.md](/Users/madhavan/Documents/CODE/AI%20Trading%20agent/frontend/README.md)
