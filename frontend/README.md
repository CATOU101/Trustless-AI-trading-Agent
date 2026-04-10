# AutoHedge AI Frontend

## Overview
The AutoHedge AI frontend is a read-only React dashboard for monitoring the autonomous backend trading system.

It does not place trades directly. The backend owns all trading logic and runs the autonomous agent loop independently.

The dashboard is focused on visibility:
- latest decision
- signed intent visibility
- identity data
- artifact history
- market indicators
- portfolio state

## What The Dashboard Shows
- agent status
- latest decision
- confidence
- explanation text
- RSI
- MA20
- current market price
- portfolio state
- trade history
- strategy votes
- leaderboard
- identity details
- current-asset trade intent
- artifact history

## Frontend Behavior
The dashboard:
- polls the backend every 60 seconds
- shows a countdown to the next decision refresh
- prevents overlapping requests
- defaults to `ethereum` for live display
- stays read-only with no coin selector or manual analyze button

Main app file:
- [src/App.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/App.js)

API client:
- [src/services/api.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/services/api.js)

## Components
- [src/components/AgentStatusCard.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/components/AgentStatusCard.js)
- [src/components/PortfolioCard.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/components/PortfolioCard.js)
- [src/components/DecisionCard.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/components/DecisionCard.js)
- [src/components/AgentVotesCard.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/components/AgentVotesCard.js)
- [src/components/IndicatorsCard.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/components/IndicatorsCard.js)
- [src/components/TradeHistory.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/components/TradeHistory.js)
- [src/components/LeaderboardCard.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/components/LeaderboardCard.js)
- [src/components/IdentityCard.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/components/IdentityCard.js)
- [src/components/IntentCard.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/components/IntentCard.js)
- [src/components/ArtifactCard.js](/Users/madhavan/.codex/worktrees/29fa/AI%20Trading%20agent/frontend/src/components/ArtifactCard.js)

## Backend Endpoints Used
The frontend reads from:
- `GET /portfolio`
- `GET /agent/decision`
- `POST /agent/analyze` as client fallback
- `GET /agents/decisions`
- `GET /agents/leaderboard`
- `GET /trades`
- `GET /market/price/{asset}`
- `GET /agent/identity`
- `GET /agent/artifacts`

Backend base URL used by the frontend code:
- `http://localhost:8000`

The backend CORS configuration allows both:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

## Project Structure
```text
frontend/
├── public/
├── src/
│   ├── components/
│   ├── services/
│   ├── App.js
│   ├── index.css
│   └── index.js
├── package.json
├── tailwind.config.js
└── README.md
```

## Running Locally
```bash
cd frontend
npm install
HOST=127.0.0.1 PORT=3000 npm start
```

Frontend URL:
- `http://127.0.0.1:3000`

## Notes
- the frontend is intentionally simple and dashboard-oriented
- the backend owns all trading logic
- the UI is designed to surface system state, not act as a trading terminal
- if the backend returns temporary fallbacks, the dashboard still renders safely
