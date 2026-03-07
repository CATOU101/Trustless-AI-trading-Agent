import React from "react";

export default function DecisionCard({ decision, confidence, reasoning, asset }) {
  return (
    <div className="bg-card rounded-xl p-5 shadow-sm border border-slate-200">
      <h2 className="text-lg font-semibold mb-3">AI Decision</h2>
      <p className="text-sm mb-1">
        Decision: <span className="font-bold">{decision || "-"} {asset ? asset.toUpperCase() : ""}</span>
      </p>
      <p className="text-sm mb-1">
        Confidence: <span className="font-medium">{typeof confidence === "number" ? confidence.toFixed(2) : "-"}</span>
      </p>
      <p className="text-sm text-slate-600">Reason: {reasoning || "No reasoning available"}</p>
    </div>
  );
}
