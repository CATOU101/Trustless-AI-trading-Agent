import React from "react";

export default function IdentityCard({ identity }) {
  const capabilities = Array.isArray(identity?.capabilities)
    ? identity.capabilities
    : [];

  return (
    <div className="bg-gray-900 rounded-xl shadow-lg p-4 text-slate-100">
      <h2 className="text-lg font-semibold mb-2">ERC-8004 Agent Identity</h2>
      <div className="space-y-2 text-sm">
        <p>
          Agent Name: <span className="font-medium">{identity?.agent_name || "-"}</span>
        </p>
        <p>
          Wallet: <span className="font-medium break-all">{identity?.wallet || "-"}</span>
        </p>
        <p>
          Agent ID: <span className="font-medium break-all">{identity?.agent_id || "-"}</span>
        </p>
        <p>
          Registry Type: <span className="font-medium">{identity?.registry_type || "-"}</span>
        </p>
        <p>
          Chain ID: <span className="font-medium">{identity?.chain_id ?? "-"}</span>
        </p>
        <p>
          Capabilities:{" "}
          <span className="font-medium">
            {capabilities.length > 0 ? capabilities.join(", ") : "-"}
          </span>
        </p>
      </div>
    </div>
  );
}
