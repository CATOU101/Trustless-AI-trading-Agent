import React from "react";

export default function TradeHistory({ trades }) {
  return (
    <div className="bg-card rounded-xl p-5 shadow-sm border border-slate-200">
      <h2 className="text-lg font-semibold mb-3">Trade History</h2>
      <div className="space-y-3">
        {(trades || []).length === 0 ? (
          <p className="text-sm text-slate-500">No trade history available.</p>
        ) : (
          trades.slice(0, 8).map((trade, idx) => (
            <div
              key={`${trade.timestamp || "t"}-${idx}`}
              className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2"
            >
              <p className="text-sm font-medium">
                {trade.timestamp || "-"} {trade.decision || "-"}{" "}
                {trade.asset ? trade.asset.toUpperCase() : "-"}
              </p>
              <p className="text-xs text-slate-600">
                Price: {trade.price ?? "-"} | Confidence:{" "}
                {typeof trade.confidence === "number"
                  ? trade.confidence.toFixed(2)
                  : "-"}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
