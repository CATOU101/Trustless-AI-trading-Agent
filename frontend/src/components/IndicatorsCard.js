import React from "react";

function fmt(value) {
  return typeof value === "number" ? value.toFixed(2) : "-";
}

export default function IndicatorsCard({ indicators, price }) {
  const hasPrice = typeof price === "number";

  return (
    <div className="bg-gray-900 rounded-xl shadow-lg p-4 text-slate-100">
      <h2 className="text-lg font-semibold mb-2">Market Indicators</h2>
      <div className="space-y-2 text-sm">
        <p>
          Current Price: <span className="font-medium">{fmt(price)}</span>
        </p>
        <p>
          Market Source: <span className="font-medium">Kraken REST</span>
        </p>
        {hasPrice ? (
          <p>
            Source: <span className="font-medium">Kraken</span>
          </p>
        ) : null}
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
