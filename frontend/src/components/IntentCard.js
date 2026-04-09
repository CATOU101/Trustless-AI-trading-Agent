import React, { useMemo } from "react";

function truncateSignature(signature) {
  if (!signature || typeof signature !== "string") return "-";
  if (signature.length <= 18) return signature;
  return `${signature.slice(0, 10)}...${signature.slice(-8)}`;
}

function pickLatestTradeIntent(artifacts, predicate) {
  return artifacts
    .filter((entry) => entry?.type === "trade_intent" && predicate(entry))
    .sort(
      (left, right) =>
        new Date(right?.timestamp || 0).getTime() -
        new Date(left?.timestamp || 0).getTime()
    )[0] || null;
}

export default function IntentCard({
  artifacts = [],
  currentAsset = "",
  chainIdFallback
}) {
  const decisionAsset = (currentAsset || "").toLowerCase();

  function renderArtifactDetails(title, selectedArtifact, fallbackAsset = "-") {
    const metadata = selectedArtifact?.metadata || {};
    const intent = metadata?.intent || {};
    const domain = metadata?.domain || {};

    const asset = selectedArtifact?.asset || intent?.asset || fallbackAsset;
    const action = selectedArtifact?.action || intent?.action || "-";
    const amount = intent?.amount ?? metadata?.amount ?? "-";
    const signature = metadata?.signature || metadata?.intent_signature || "-";
    const chainId = domain?.chainId ?? chainIdFallback ?? "-";

    return (
      <div className="space-y-2 text-sm">
        <h3 className="text-sm font-medium text-slate-300">{title}</h3>
        {!selectedArtifact ? (
          <p className="text-slate-400">
            No trade intent generated for this asset yet.
          </p>
        ) : (
          <>
            <p>
              Asset: <span className="font-medium">{asset}</span>
            </p>
            <p>
              Action: <span className="font-medium">{action}</span>
            </p>
            <p>
              Amount: <span className="font-medium">{amount}</span>
            </p>
            <p>
              Signature: <span className="font-medium">{truncateSignature(signature)}</span>
            </p>
            <p>
              Domain Chain ID: <span className="font-medium">{chainId}</span>
            </p>
          </>
        )}
      </div>
    );
  }

  const selectedCurrentArtifact = useMemo(() => {
    if (!Array.isArray(artifacts) || artifacts.length === 0 || !decisionAsset) {
      return null;
    }
    return pickLatestTradeIntent(
      artifacts,
      (entry) => String(entry?.asset || "").toLowerCase() === decisionAsset
    );
  }, [artifacts, decisionAsset]);

  return (
    <div className="bg-gray-900 rounded-xl shadow-lg p-4 text-slate-100">
      <h2 className="text-lg font-semibold mb-2">EIP-712 Signed Trade Intent</h2>
      <div className="space-y-4">
        {renderArtifactDetails(
          "Trade Intent (current asset)",
          selectedCurrentArtifact,
          decisionAsset || "-"
        )}
      </div>
    </div>
  );
}
