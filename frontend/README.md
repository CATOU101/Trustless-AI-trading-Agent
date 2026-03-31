# AutoHedge AI Frontend

The AutoHedge AI frontend is a read-only React dashboard for monitoring the autonomous backend trading system.

It does not trigger trading manually.

The backend runs the agent automatically. The frontend only displays state and refreshes on a schedule.

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

## Frontend Behavior

The dashboard:
- polls the backend every 60 seconds
- prevents overlapping requests
- defaults to `bitcoin` for live display
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

## Backend Endpoints Used

The frontend reads from these backend endpoints:
- `GET /portfolio`
- `GET /agent/decision`
- `POST /agent/analyze` as fallback path in the client
- `GET /agents/decisions`
- `GET /agents/leaderboard`
- `GET /trades`
- `GET /market/price/{asset}`

Backend base URL expected by the frontend:
- `http://localhost:8000`

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

## Run The Frontend

```bash
cd frontend
npm install
npm start
```

Frontend URL:
- `http://localhost:3000`

## Development Notes

- The frontend is intentionally simple and dashboard-oriented.
- The backend owns all trading logic.
- The UI is designed to surface system state, not to act as a trading terminal.
- If the backend returns temporary fallbacks, the dashboard still renders safely.
