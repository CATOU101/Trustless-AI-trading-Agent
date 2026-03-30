import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import AgentStatusCard from "./components/AgentStatusCard";
import AgentVotesCard from "./components/AgentVotesCard";
import PortfolioCard from "./components/PortfolioCard";
import DecisionCard from "./components/DecisionCard";
import IndicatorsCard from "./components/IndicatorsCard";
import LeaderboardCard from "./components/LeaderboardCard";
import TradeHistory from "./components/TradeHistory";
import {
  getAgentVotes,
  getAgentLeaderboard,
  getLatestDecision,
  getMarketData,
  getPortfolio,
  getTradeHistory
} from "./services/api";

const DEFAULT_ASSET = "bitcoin";

export default function App() {
  const [decisionData, setDecisionData] = useState(null);
  const [votesData, setVotesData] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [portfolioData, setPortfolioData] = useState(null);
  const [tradeHistory, setTradeHistory] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const requestInFlightRef = useRef(false);

  const refreshDashboard = useCallback(async () => {
    if (requestInFlightRef.current) return;
    requestInFlightRef.current = true;
    setLoading(true);
    setError("");

    try {
      const [decision, votes, market, portfolio, trades, board] = await Promise.all([
        getLatestDecision(DEFAULT_ASSET),
        getAgentVotes(DEFAULT_ASSET).catch(() => null),
        getMarketData(DEFAULT_ASSET).catch(() => null),
        getPortfolio().catch(() => null),
        getTradeHistory().catch(() => []),
        getAgentLeaderboard().catch(() => [])
      ]);

      setDecisionData(decision);
      setVotesData(votes);
      setMarketData(market);
      setPortfolioData(decision?.portfolio || portfolio || null);
      setLeaderboard(Array.isArray(board) ? board : decision?.leaderboard || []);

      const fallbackTrade = {
        timestamp: new Date().toISOString(),
        asset: decision?.asset,
        decision: decision?.decision,
        price: decision?.portfolio?.portfolio_value,
        confidence: decision?.confidence
      };
      setTradeHistory(Array.isArray(trades) && trades.length > 0 ? trades : [fallbackTrade]);
    } catch (err) {
      setError(err.message || "Failed to fetch dashboard data.");
    } finally {
      requestInFlightRef.current = false;
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshDashboard();
    const intervalId = setInterval(refreshDashboard, 60000);
    return () => clearInterval(intervalId);
  }, [refreshDashboard]);

  const currentAsset = useMemo(
    () => decisionData?.asset || votesData?.asset || DEFAULT_ASSET,
    [decisionData, votesData]
  );
  const status = {
    running: !error,
    asset: currentAsset,
    message: loading
      ? "Refreshing autonomous agent state."
      : "Backend agent is scanning markets automatically every 60 seconds."
  };

  return (
    <main className="min-h-screen p-6 md:p-10">
      <div className="max-w-6xl mx-auto space-y-6">
        <header>
          <h1 className="text-2xl md:text-3xl font-bold text-ink">
            AutoHedge AI
          </h1>
          <p className="text-slate-600 mt-1">
            Read-only dashboard for the backend trading system
          </p>
        </header>

        {error ? <p className="text-sm text-red-600">{error}</p> : null}
        {loading ? <p className="text-sm text-slate-500">Loading dashboard...</p> : null}

        <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <AgentStatusCard status={status} />
          <PortfolioCard portfolio={portfolioData} asset={currentAsset} />
          <DecisionCard
            decision={decisionData?.decision}
            confidence={decisionData?.confidence}
            reasoning={decisionData?.reasoning}
            asset={currentAsset}
          />
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <AgentVotesCard votes={votesData?.agent_votes || decisionData?.agent_votes} />
          <IndicatorsCard
            indicators={decisionData?.indicators}
            price={marketData?.price_usd}
          />
        </section>

        <section>
          <TradeHistory trades={tradeHistory} />
        </section>

        <section>
          <LeaderboardCard leaderboard={leaderboard} />
        </section>
      </div>
    </main>
  );
}
