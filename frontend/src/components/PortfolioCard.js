import React from "react";

function formatNumber(value) {
  if (typeof value !== "number") return "-";
  return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

export default function PortfolioCard({ portfolio, asset }) {
  const holdings =
    portfolio?.[asset] ??
    (portfolio?.assets && asset ? portfolio.assets[asset] : undefined);

  return (
    <div className="bg-card rounded-xl p-5 shadow-sm border border-slate-200">
      <h2 className="text-lg font-semibold mb-3">Portfolio</h2>
      <div className="space-y-2 text-sm">
        <p>
          Cash Balance: <span className="font-medium">${formatNumber(portfolio?.cash_balance)}</span>
        </p>
        <p>
          {asset || "Asset"} Holdings: <span className="font-medium">{formatNumber(holdings)}</span>
        </p>
        <p>
          Total Value: <span className="font-semibold text-accent">${formatNumber(portfolio?.portfolio_value)}</span>
        </p>
      </div>
    </div>
  );
}
