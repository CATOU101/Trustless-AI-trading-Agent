import React from "react";

export default function AgentStatusCard({ status }) {
  return (
    <div className="bg-card rounded-xl p-5 shadow-sm border border-slate-200">
      <h2 className="text-lg font-semibold mb-3">Agent Status</h2>
      <div className="space-y-2 text-sm">
        <p>
          Running:{" "}
          <span className="font-medium">{status?.running ? "Yes" : "No"}</span>
        </p>
        <p>
          Asset Focus:{" "}
          <span className="font-medium">{status?.asset?.toUpperCase?.() || "-"}</span>
        </p>
        <p className="text-slate-600">
          {status?.message || "Monitoring markets and updating automatically."}
        </p>
      </div>
    </div>
  );
}
