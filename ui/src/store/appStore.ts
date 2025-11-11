import { create } from "zustand";
import { Invoice, Contract, ExtractionMeta, Finding, ReconcileResponse } from "../types/api";

interface AppState {
  invoice: Invoice | null;
  contract: Contract | null;
  extractionMeta: ExtractionMeta[];
  reconcileResult: ReconcileResponse | null;
  note: string | null;

  loading: boolean;
  error: string | null;
  highlightedFieldPath: string | null;
  highlightedFindingIdx: number | null;
  autoProcessing: boolean;

  setInvoice: (invoice: Invoice | null) => void;
  setContract: (contract: Contract | null) => void;
  setExtractionMeta: (meta: ExtractionMeta[]) => void;
  setReconcileResult: (result: ReconcileResponse | null) => void;
  setNote: (note: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setHighlightedFieldPath: (path: string | null) => void;
  setHighlightedFindingIdx: (idx: number | null) => void;
  setAutoProcessing: (autoProcessing: boolean) => void;
  reset: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  invoice: null,
  contract: null,
  extractionMeta: [],
  reconcileResult: null,
  note: null,
  loading: false,
  error: null,
  highlightedFieldPath: null,
  highlightedFindingIdx: null,
  autoProcessing: false,

  setInvoice: (invoice) => set({ invoice }),
  setContract: (contract) => set({ contract }),
  setExtractionMeta: (extractionMeta) => set({ extractionMeta }),
  setReconcileResult: (reconcileResult) => set({ reconcileResult }),
  setNote: (note) => set({ note }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setHighlightedFieldPath: (highlightedFieldPath) => set({ highlightedFieldPath }),
  setHighlightedFindingIdx: (highlightedFindingIdx) => set({ highlightedFindingIdx }),
  setAutoProcessing: (autoProcessing) => set({ autoProcessing }),
  reset: () =>
    set({
      invoice: null,
      contract: null,
      extractionMeta: [],
      reconcileResult: null,
      note: null,
      loading: false,
      error: null,
      highlightedFieldPath: null,
      highlightedFindingIdx: null,
      autoProcessing: false,
    }),
}));

