import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import PortfolioCard from "./components/PortfolioCard";
import DecisionCard from "./components/DecisionCard";
import IndicatorsCard from "./components/IndicatorsCard";
import TradeHistory from "./components/TradeHistory";
import { getAgentDecision, getPortfolio, getTradeHistory } from "./services/api";

const DEFAULT_COIN = "bitcoin";

export default function App() {
  const [coin, setCoin] = useState(DEFAULT_COIN);
  const [decisionData, setDecisionData] = useState(null);
  const [portfolioData, setPortfolioData] = useState(null);
  const [tradeHistory, setTradeHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const requestInFlightRef = useRef(false);

  const refreshDashboard = useCallback(async () => {
    if (requestInFlightRef.current) return;
    requestInFlightRef.current = true;
    setLoading(true);
    setError("");

    try {
      const [decision, portfolio, trades] = await Promise.all([
        getAgentDecision(coin),
        getPortfolio().catch(() => null),
        getTradeHistory().catch(() => [])
      ]);

      setDecisionData(decision);
      setPortfolioData(decision?.portfolio || portfolio || null);

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
  }, [coin]);

  useEffect(() => {
    refreshDashboard();
    const intervalId = setInterval(refreshDashboard, 60000);
    return () => clearInterval(intervalId);
  }, [refreshDashboard]);

  const currentAsset = useMemo(() => decisionData?.asset || coin, [decisionData, coin]);

  return (
    <main className="min-h-screen p-6 md:p-10">
      <div className="max-w-6xl mx-auto space-y-6">
        <header className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-ink">Explainable AI Trading Agent</h1>
            <p className="text-slate-600 mt-1">Live decision dashboard</p>
          </div>
          <div className="flex items-center gap-3">
            <label htmlFor="coin" className="text-sm text-slate-700">Coin</label>
            <input
              id="coin"
              value={coin}
              onChange={(event) => setCoin(event.target.value.toLowerCase())}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="bitcoin"
            />
            <button
              onClick={refreshDashboard}
              className="rounded-lg bg-accent text-white text-sm px-4 py-2 hover:opacity-90"
              type="button"
            >
              Refresh
            </button>
          </div>
        </header>

        {error ? <p className="text-sm text-red-600">{error}</p> : null}
        {loading ? <p className="text-sm text-slate-500">Loading dashboard...</p> : null}

        <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <PortfolioCard portfolio={portfolioData} asset={currentAsset} />
          <DecisionCard
            decision={decisionData?.decision}
            confidence={decisionData?.confidence}
            reasoning={decisionData?.reasoning}
            asset={currentAsset}
          />
          <IndicatorsCard indicators={decisionData?.indicators} />
        </section>

        <section>
          <TradeHistory trades={tradeHistory} />
        </section>
      </div>
    </main>
  );
}
