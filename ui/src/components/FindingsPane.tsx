import React from "react";
import { useAppStore } from "../store/appStore";
import { apiClient } from "../api/client";
import "../styles/components.css";

export const FindingsPane: React.FC = () => {
  const {
    invoice,
    contract,
    reconcileResult,
    setReconcileResult,
    setLoading,
    setError,
    setHighlightedFindingIdx,
  } = useAppStore();

  const handleReconcile = async () => {
    if (!invoice || !contract) {
      setError("Please extract invoice and contract first");
      return;
    }

    try {
      setLoading(true);
      const result = await apiClient.reconcile(invoice, contract);
      setReconcileResult(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reconciliation failed");
    } finally {
      setLoading(false);
    }
  };

  if (!reconcileResult) {
    return (
      <div className="findings-pane">
        <h3>Findings</h3>
        <button onClick={handleReconcile} className="btn-primary">
          Run Reconciliation
        </button>
      </div>
    );
  }

  const { summary, findings } = reconcileResult;
  const statusText = summary.pass ? "PASSED" : "FAILED";

  return (
    <div className="findings-pane">
      <h3>Findings</h3>

      <div className="summary-box" style={summary.pass ? { borderColor: "var(--primary)" } : { borderColor: "var(--danger)" }}>
        <div className="summary-status">
          <strong>{statusText}</strong>
        </div>
        <div className="summary-stats">
          <span className="stat">
            Major: <strong>{summary.major_count}</strong>
          </span>
          <span className="stat">
            Minor: <strong>{summary.minor_count}</strong>
          </span>
          <span className="stat">
            Total: <strong>{summary.total_count}</strong>
          </span>
        </div>
      </div>

      {findings.length === 0 ? (
        <div className="placeholder">No variances detected. Invoice matches contract terms.</div>
      ) : (
        <table className="findings-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Severity</th>
              <th>Type</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {findings.map((finding, idx) => (
              <tr
                key={idx}
                className={finding.severity === "MAJOR" ? "finding-major" : "finding-minor"}
                onMouseEnter={() => setHighlightedFindingIdx(idx)}
                onMouseLeave={() => setHighlightedFindingIdx(null)}
              >
                <td>{idx + 1}</td>
                <td>
                  <strong>
                    {finding.severity === "MAJOR" ? "MAJOR" : "MINOR"}
                  </strong>
                </td>
                <td>{finding.type}</td>
                <td className="details">{finding.details.substring(0, 80)}...</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <button onClick={handleReconcile} className="btn-primary">
        Re-run Reconciliation
      </button>
    </div>
  );
};

