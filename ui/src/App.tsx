import React, { useEffect } from "react";
import { useAppStore } from "./store/appStore";
import { apiClient } from "./api/client";
import { UploadPane } from "./components/UploadPane";
import { DocViewer } from "./components/DocViewer";
import { ExtractionPane } from "./components/ExtractionPane";
import { FindingsPane } from "./components/FindingsPane";
import { NoteDisplay } from "./components/NoteDisplay";
import "./styles/App.css";

function App() {
  const { error, setError, loading } = useAppStore();

  useEffect(() => {
    apiClient.health().catch(() => {
      setError("Could not connect to API. Is backend running on http://localhost:8000?");
    });
  }, [setError]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>PactProof</h1>
        <p className="subtitle">Compliance Invoice Reconciliation</p>
      </header>

      {error && (
        <div className="error-banner">
          <strong>⚠️ Error:</strong> {error}
          <button onClick={() => setError(null)} className="close-btn">
            ✕
          </button>
        </div>
      )}

      {loading && <div className="loading-overlay">Processing...</div>}

      <div className="app-container">
        <div className="left-column">
          <section className="section">
            <UploadPane />
          </section>
          <section className="section">
            <DocViewer />
          </section>
        </div>

        <div className="right-column">
          <section className="section scrollable">
            <ExtractionPane />
          </section>
          <section className="section scrollable">
            <FindingsPane />
          </section>
          <section className="section scrollable">
            <NoteDisplay />
          </section>
        </div>
      </div>

      <footer className="app-footer">
        <p>
          PactProof © 2025 | Deterministic, auditable invoice reconciliation |{" "}
          <a href="https://landing.ai" target="_blank" rel="noopener noreferrer">
            Powered by LandingAI
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;

