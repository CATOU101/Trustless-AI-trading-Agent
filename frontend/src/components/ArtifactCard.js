import React from "react";

export default function ArtifactCard({ artifacts }) {
  const lastFive = Array.isArray(artifacts) ? artifacts.slice(-5).reverse() : [];

  return (
    <div className="bg-gray-900 rounded-xl shadow-lg p-4 text-slate-100">
      <h2 className="text-lg font-semibold mb-2">Validation Artifacts</h2>
      <div className="space-y-3">
        {lastFive.length === 0 ? (
          <p className="text-sm text-slate-400">No artifacts available.</p>
        ) : (
          lastFive.map((artifact, index) => (
            <div
              key={`${artifact?.artifact_hash || "artifact"}-${index}`}
              className="rounded-lg bg-gray-800 border border-gray-700 p-3"
            >
              <p className="text-sm">
                Type: <span className="font-medium">{artifact?.type || "-"}</span>
              </p>
              <p className="text-sm">
                Asset: <span className="font-medium">{artifact?.asset || "-"}</span>
              </p>
              <p className="text-sm">
                Action: <span className="font-medium">{artifact?.action || "-"}</span>
              </p>
              <p className="text-sm">
                Validation:{" "}
                <span className="font-medium">{artifact?.validation_status || "-"}</span>
              </p>
              <p className="text-sm break-all">
                Hash: <span className="font-medium">{artifact?.artifact_hash || "-"}</span>
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Timestamp: {artifact?.timestamp || "-"}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
