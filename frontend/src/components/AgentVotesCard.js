import React from "react";

export default function AgentVotesCard({ votes }) {
  return (
    <div className="bg-card rounded-xl p-5 shadow-sm border border-slate-200">
      <h2 className="text-lg font-semibold mb-3">Agent Votes</h2>
      <div className="space-y-3">
        {(votes || []).length === 0 ? (
          <p className="text-sm text-slate-500">No agent votes available.</p>
        ) : (
          votes.map((vote) => (
            <div
              key={vote.agent}
              className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2"
            >
              <p className="text-sm font-semibold">{vote.agent}</p>
              <p className="text-sm">
                {vote.action}{" "}
                <span className="text-slate-500">
                  ({typeof vote.confidence === "number"
                    ? vote.confidence.toFixed(2)
                    : "-"})
                </span>
              </p>
              <p className="text-xs text-slate-600">{vote.reason || "-"}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
