import React from "react";

export default function LeaderboardCard({ leaderboard }) {
  return (
    <div className="bg-card rounded-xl p-5 shadow-sm border border-slate-200">
      <h2 className="text-lg font-semibold mb-3">Agent Leaderboard</h2>
      <div className="space-y-3">
        {(leaderboard || []).length === 0 ? (
          <p className="text-sm text-slate-500">No agent performance data yet.</p>
        ) : (
          leaderboard.map((entry) => (
            <div
              key={entry.agent}
              className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2"
            >
              <p className="text-sm font-semibold">{entry.agent}</p>
              <p className="text-xs text-slate-600">
                Trades: {entry.total_trades} | Win Rate:{" "}
                {typeof entry.win_rate === "number"
                  ? (entry.win_rate * 100).toFixed(1)
                  : "-"}
                %
              </p>
              <p className="text-xs text-slate-600">
                Profit: {entry.profit ?? "-"} | Avg Return: {entry.average_return ?? "-"}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
