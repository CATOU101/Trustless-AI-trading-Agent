import React from "react";

function truncateSignature(signature) {
  if (!signature || typeof signature !== "string") return "-";
  if (signature.length <= 18) return signature;
  return `${signature.slice(0, 10)}...${signature.slice(-8)}`;
}

export default function IntentCard({ artifact, chainIdFallback }) {
  const metadata = artifact?.metadata || {};
  const intent = metadata?.intent || {};
  const domain = metadata?.domain || {};

  const asset = artifact?.asset || intent?.asset || "-";
  const action = artifact?.action || intent?.action || "-";
  const amount = intent?.amount ?? metadata?.amount ?? "-";
  const signature = metadata?.signature || metadata?.intent_signature || "-";
  const chainId = domain?.chainId ?? chainIdFallback ?? "-";

  return (
    <div className="bg-gray-900 rounded-xl shadow-lg p-4 text-slate-100">
      <h2 className="text-lg font-semibold mb-2">EIP-712 Signed Trade Intent</h2>
      {!artifact ? (
        <p className="text-sm text-slate-400">No trade intent artifact available yet.</p>
      ) : (
        <div className="space-y-2 text-sm">
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
        </div>
      )}
    </div>
  );
}
