import React from "react";

export default function AgentStatusCard({ status }) {
  return (
    <div className="bg-gray-900 rounded-xl shadow-lg p-4 text-slate-100">
      <h2 className="text-lg font-semibold mb-2">Autonomous Runner Status</h2>
      <div className="space-y-2 text-sm">
        <p>
          Running: <span className="font-medium">true</span>
        </p>
        <p>
          Scan Interval: <span className="font-medium">60s</span>
        </p>
        <p>
          Mode: <span className="font-medium">Autonomous</span>
        </p>
        <p>
          Execution: <span className="font-medium">Kraken CLI / Sandbox fallback</span>
        </p>
        <p>
          Asset Focus: <span className="font-medium">{status?.asset?.toUpperCase?.() || "-"}</span>
        </p>
        <p className="text-slate-300">
          {status?.message || "Monitoring markets and updating automatically."}
        </p>
      </div>
    </div>
  );
}
