import React, { useState } from "react";
import { apiClient } from "../api/client";
import { useAppStore } from "../store/appStore";
import "../styles/components.css";

export const UploadPane: React.FC = () => {
  const [invoiceFile, setInvoiceFile] = useState<File | null>(null);
  const [contractFile, setContractFile] = useState<File | null>(null);

  const { 
    setLoading, 
    setError, 
    setInvoice, 
    setContract, 
    setExtractionMeta,
    setReconcileResult,
    setNote,
    autoProcessing,
    setAutoProcessing,
    invoice,
    contract
  } = useAppStore();

  const handleInvoiceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      setInvoiceFile(e.target.files[0]);
    }
  };

  const handleContractChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      setContractFile(e.target.files[0]);
    }
  };

  const handleExtract = async () => {
    if (!invoiceFile || !contractFile) {
      setError("Please select both invoice and contract files");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const invoiceResult = await apiClient.parseExtractInvoice(invoiceFile);
      const parsedInvoice = invoiceResult.invoice || null;
      setInvoice(parsedInvoice);

      const contractResult = await apiClient.parseExtractContract(contractFile);
      const parsedContract = contractResult.contract || null;
      setContract(parsedContract);

      const allMeta = [...invoiceResult.meta, ...contractResult.meta];
      setExtractionMeta(allMeta);

      if (autoProcessing && parsedInvoice && parsedContract) {
        try {
          const reconcileResult = await apiClient.reconcile(parsedInvoice, parsedContract);
          setReconcileResult(reconcileResult);

          const noteResponse = await apiClient.draftNote({
            invoice: parsedInvoice,
            contract: parsedContract,
            reconcile: reconcileResult,
          });
          setNote(noteResponse.markdown);
        } catch (autoErr) {
          setError(autoErr instanceof Error ? autoErr.message : "Auto-processing failed");
        }
      }

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Extraction failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-pane">
      <h2>Upload Documents</h2>

      <div className="upload-section">
        <label>
          <strong>Invoice (JPG/PNG/PDF)</strong>
          <input type="file" accept="image/*,.pdf" onChange={handleInvoiceChange} />
          {invoiceFile && <span className="file-name">{invoiceFile.name}</span>}
        </label>
      </div>

      <div className="upload-section">
        <label>
          <strong>Contract/SOW (JSON/PDF)</strong>
          <input type="file" accept=".json,.pdf" onChange={handleContractChange} />
          {contractFile && <span className="file-name">{contractFile.name}</span>}
        </label>
      </div>

      <div className="toggle-section">
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={autoProcessing}
            onChange={(e) => setAutoProcessing(e.target.checked)}
            className="toggle-checkbox"
          />
          <span className="toggle-text">Auto-process (reconcile & generate notes)</span>
        </label>
      </div>

      <button onClick={handleExtract} className="btn-primary">
        Parse & Extract
      </button>
    </div>
  );
};

