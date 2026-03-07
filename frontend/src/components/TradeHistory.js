import React from "react";

export default function TradeHistory({ trades }) {
  return (
    <div className="bg-card rounded-xl p-5 shadow-sm border border-slate-200">
      <h2 className="text-lg font-semibold mb-3">Trade History</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="text-left border-b border-slate-200">
              <th className="py-2">Time</th>
              <th className="py-2">Asset</th>
              <th className="py-2">Decision</th>
              <th className="py-2">Price</th>
              <th className="py-2">Confidence</th>
            </tr>
          </thead>
          <tbody>
            {(trades || []).length === 0 ? (
              <tr>
                <td className="py-3 text-slate-500" colSpan={5}>No trade history available.</td>
              </tr>
            ) : (
              trades.map((trade, idx) => (
                <tr key={`${trade.timestamp || "t"}-${idx}`} className="border-b border-slate-100">
                  <td className="py-2">{trade.timestamp || "-"}</td>
                  <td className="py-2">{trade.asset || "-"}</td>
                  <td className="py-2">{trade.decision || "-"}</td>
                  <td className="py-2">{trade.price ?? "-"}</td>
                  <td className="py-2">{typeof trade.confidence === "number" ? trade.confidence.toFixed(2) : "-"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
