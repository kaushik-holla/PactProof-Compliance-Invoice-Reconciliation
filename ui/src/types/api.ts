/**
 * TypeScript interfaces matching Pydantic models
 */

export interface Box {
  page: number;
  left: number;
  top: number;
  right: number;
  bottom: number;
}

export interface ExtractionMeta {
  field_path: string;
  boxes: Box[];
  page?: number;
}

export interface InvoiceLine {
  description: string;
  quantity: number;
  unit_price?: number;
  total_price: number;
  tax?: number;
  sku?: string;
}

export interface Invoice {
  client_name: string;
  client_address?: string;
  seller_name: string;
  seller_address?: string;
  invoice_number: string;
  invoice_date: string;
  due_date?: string;
  items: InvoiceLine[];
  subtotal: {
    tax?: number;
    discount?: number;
    total: number;
  };
  currency?: string;
  net_terms?: string;
  tax_rate?: number;
}

export interface ContractLine {
  description: string;
  sku?: string;
  unit_price: number;
  max_quantity?: number;
  discount_pct?: number;
  tax_rate?: number;
}

export interface Contract {
  vendor_name: string;
  client_name: string;
  contract_id: string;
  currency?: string;
  net_terms?: string;
  early_payment_discount?: number;
  default_tax_rate: number;
  allowed_variance_pct: number;
  line_items: ContractLine[];
}

export type FindingType =
  | "UNIT_PRICE_VARIANCE"
  | "QUANTITY_OVERFLOW"
  | "UNKNOWN_LINE"
  | "CURRENCY_MISMATCH"
  | "TERMS_MISMATCH"
  | "TAX_MISMATCH";

export type FindingSeverity = "MAJOR" | "MINOR";

export interface Finding {
  type: FindingType;
  severity: FindingSeverity;
  details: string;
  invoice_line_idx?: number;
  contract_line_idx?: number;
  evidence_page?: number;
  evidence_boxes: Box[];
}

export interface ReconcileSummary {
  pass: boolean;
  major_count: number;
  minor_count: number;
  total_count: number;
}

export interface ReconcileResponse {
  summary: ReconcileSummary;
  findings: Finding[];
}

export interface ParseResult {
  pages: number;
  markdown?: string;
}

export interface ExtractionResponse {
  invoice?: Invoice;
  contract?: Contract;
  meta: ExtractionMeta[];
  parse: ParseResult;
  file_url: string;
  file_path: string;
}

export interface NoteGenerationRequest {
  invoice: Invoice;
  contract: Contract;
  reconcile: ReconcileResponse;
}

export interface NoteGenerationResponse {
  markdown: string;
  html?: string;
}

// Utility functions
export function normalizeCoordinate(value: number): number {
  return Math.max(0, Math.min(1, value));
}

export function boxToPixels(box: Box, containerWidth: number, containerHeight: number) {
  return {
    left: box.left * containerWidth,
    top: box.top * containerHeight,
    width: (box.right - box.left) * containerWidth,
    height: (box.bottom - box.top) * containerHeight,
  };
}

