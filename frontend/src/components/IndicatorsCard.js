import React from "react";

function fmt(value) {
  return typeof value === "number" ? value.toFixed(2) : "-";
}

export default function IndicatorsCard({ indicators }) {
  return (
    <div className="bg-card rounded-xl p-5 shadow-sm border border-slate-200">
      <h2 className="text-lg font-semibold mb-3">Market Indicators</h2>
      <div className="space-y-2 text-sm">
        <p>
          RSI: <span className="font-medium">{fmt(indicators?.rsi)}</span>
        </p>
        <p>
          20-day Moving Average: <span className="font-medium">{fmt(indicators?.ma20)}</span>
        </p>
      </div>
    </div>
  );
}
