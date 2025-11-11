# PactProof - Compliance Invoice Reconciliation

**Automatically compare supplier invoices to governing contracts, flag variances, and generate auditable exception notes in seconds.**

## Problem

Accounts Payable (AP) is the last gate before cash goes out. Invoices often drift from the deal: wrong unit prices, unapproved items, quantity overages, wrong tax/currency, or ignored payment terms. Manual, spreadsheet-driven checks are slow and error-prone, so overpayments slip through or require costly rework—and the audit trail is thin.

PactProof changes the game: deterministic, auditable checks on every invoice vs contract/SOW in < 8 seconds, with each finding linked to the source (page/box) for evidence.


## What is PactProof?

PactProof is the contract-truth layer for AP. It reads the invoice and the contract/SOW, lines them up, and runs deterministic checks—unit-price variance, quantity caps, unknown line-items, currency/terms/tax. If something’s off, it generates a CFO-ready exception note that links each claim back to the exact spot on the documents.

Where it fits: Shines on services/SOW and order-form invoices where POs/receipts don’t capture the real deal.

## Quick Start

### Prerequisites

**Required:**
- Python 3.10+ with pip
- Node.js 18+ with npm
- Git (for cloning the repository)

**API Keys:**
- **LandingAI ADE API Key** (required for real document extraction)
  - Get yours at: https://landing.ai
  - Or use `APP_MODE=STUB` for testing with mock data
- **Google Gemini API Key**
  - Get yours at: https://aistudio.google.com

**Operating Systems:**
- macOS, Linux, or Windows (WSL recommended for Windows)

**Python Dependencies:**
- FastAPI, Pydantic, RapidFuzz, Jinja2, Pillow, requests, python-dotenv
- (Auto-installed via `requirements.txt`)

**Node Dependencies:**
- React 18, TypeScript, Vite, Zustand, Axios
- (Auto-installed via `npm install`)

### Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your API keys (or leave blank for STUB mode)

# Run backend
cd backend
python app.py
# API will be available at http://localhost:8000
```

### Frontend Setup

```bash
# Install dependencies
cd ui
npm install

# Run development server
npm run dev
# UI will be available at http://localhost:5173
```

## Features

### Core Capabilities

1. **Invoice Extraction**
   - Parse invoice images (JPG/PNG) or PDFs
   - Automatically extract vendor, invoice number, dates, line items, totals
   - Uses LandingAI ADE for vision-powered field extraction
   - Returns grounding boxes for each field (click to highlight)

2. **Contract/SOW Matching**
   - Upload Contract JSON or PDF
   - Extract structured fields: vendor name, line items, unit prices, terms
   - Support for max quantities, discounts, tax rates

3. **Deterministic Reconciliation**
   - **Line Matching:** SKU exact-match or fuzzy description matching (≥85% confidence)
   - **Price Checks:** Detect unit price variance exceeding allowed percentage (default 2%)
   - **Quantity Checks:** Flag overages against contract max quantity
   - **Currency Check:** Match invoice vs contract currency
   - **Terms Check:** Match net terms (Net 30, Net 60, etc.)
   - **Unknown Lines:** Flag invoice lines with no contract match

4. **Exception Notes**
   - Generate CFO-friendly markdown reports
   - Summary: pass/fail status, major/minor issue counts
   - Detailed findings with evidence references
   - One-click copy to clipboard and extract as PDF options
   - LLM polished using Gemini 2.0 flash model for better language

5. **Web UI**
   - Upload invoice image + contract JSON
   - Live extraction preview
   - Click to highlight extracted fields on document
   - Reconciliation findings table (color-coded by severity)
   - Exception note generator & clipboard copy
   - Responsive design, mobile-friendly

## Architecture

```
[React+TS UI]  ──────────  [FastAPI Backend]
   ↓                            ↓
Components                 Endpoints:
- UploadPane              • POST /parse_extract/invoice
- DocViewer               • POST /parse_extract/contract
- ExtractionPane          • POST /reconcile
- FindingsPane            • POST /draft_note
- NoteDisplay             • GET /uploads/{file}
   ↓                            ↓
 Zustand Store             Services:
- invoice                  • ADEClient (LandingAI ADE)
- contract                 • ReconcileEngine (rules)
- findings                 • NoteGenerator (Jinja2)
- note
```

## Tech Stack

### Backend
- **Framework:** FastAPI + Uvicorn
- **Validation:** Pydantic v2
- **Vision AI:** LandingAI ADE (Parse + Extract)
- **String Matching:** RapidFuzz
- **Templates:** Jinja2
- **LLM (optional):** Google Gemini

### Frontend
- **Framework:** React 18 + TypeScript
- **Build:** Vite
- **State:** Zustand
- **HTTP:** Axios
- **Styling:** CSS3

### Infrastructure
- **Local:** Python + Node.js


## Known Limitations & Future Work

### Current Limitations

**Document Processing:**
- **PDF Contract Parsing:** Limited PDF support; JSON contracts recommended for now
- **Image Quality:** Best results with high-resolution scans (300+ DPI); low-quality images may fail
- **Language Support:** English only; no multi-language OCR or translation
- **Document Types:** Optimized for standard invoices/SOWs; custom formats may require schema tuning

**Matching & Reconciliation:**
- **SKU Matching:** Fuzzy description matching is best-effort; exact SKU matching preferred when available
- **Fixed Thresholds:** 85% fuzzy match threshold and 2% variance are configurable but not adaptive per vendor
- **Line Item Limits:** Performance tested up to ~50 line items per document
- **Multi-Currency:** Basic currency matching only; no real-time exchange rates or conversion
- **Tax Calculations:** Simple tax rate comparison; no complex jurisdiction-based tax rules
- **2-Way Matching:** Invoice ↔ Contract only (no Purchase Order or Goods Receipt validation)

**System & Architecture:**
- **No Persistence:** All data is ephemeral; no database or file storage beyond uploads directory
- **No User Management:** Single-user application; no authentication, authorization, or multi-tenancy
- **No Audit Trail:** No persistent logging of decisions, approvals, or changes to database
- **Manual Upload Only:** Requires manual file selection; no automated inbox monitoring
- **No Batch Processing:** One invoice at a time; no bulk upload or parallel processing
- **In-Memory State:** Application state resets on page refresh; no session persistence

## Credits

- Invoice dataset: Kaggle (https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr)
- Vision AI: LandingAI ADE
- LLM: Google Gemini
- Built for Financial AI Hackathon Championship - 2025

**PactProof: Compliance at Speed**

