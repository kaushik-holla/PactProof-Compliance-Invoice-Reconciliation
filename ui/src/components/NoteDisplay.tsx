import React, { useState } from "react";
import { useAppStore } from "../store/appStore";
import { apiClient } from "../api/client";
import "../styles/components.css";

export const NoteDisplay: React.FC = () => {
  const { invoice, contract, reconcileResult, note, setNote, setLoading, setError } = useAppStore();
  const [copied, setCopied] = useState(false);
  const [exporting, setExporting] = useState(false);

  const handleDraftNote = async () => {
    if (!invoice || !contract || !reconcileResult) {
      setError("Please complete reconciliation first");
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.draftNote({
        invoice,
        contract,
        reconcile: reconcileResult,
      });
      setNote(response.markdown);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Note generation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyToClipboard = async () => {
    if (!note) return;
    try {
      await navigator.clipboard.writeText(note);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      setError("Failed to copy to clipboard");
    }
  };

  const handleExportPdf = async () => {
    if (!note) return;
    try {
      setExporting(true);
      const blob = await apiClient.exportNotePdf(note, invoice?.invoice_number);
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, -5);
      a.download = `compliance_report_${invoice?.invoice_number || "note"}_${timestamp}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "PDF export failed");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="note-display">
      <h3>Exception Note</h3>

      {note ? (
        <>
          <div className="note-content">
            <pre>{note}</pre>
          </div>
          <div className="note-actions">
            <button
              onClick={handleCopyToClipboard}
              className="btn-secondary"
              style={{ backgroundColor: copied ? "var(--primary)" : undefined, color: copied ? "#000" : undefined }}
            >
              {copied ? "Copied!" : "Copy to Clipboard"}
            </button>
            <button
              onClick={handleExportPdf}
              className="btn-secondary"
              disabled={exporting}
            >
              {exporting ? "Exporting..." : "Export as PDF"}
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="placeholder">Draft an exception note from your findings</div>
          <button onClick={handleDraftNote} className="btn-primary">
            Draft Exception Note
          </button>
        </>
      )}
    </div>
  );
};

