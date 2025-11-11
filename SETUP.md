# PactProof Setup Guide


### 1. Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)
- macOS, Linux, or Windows (WSL)

### 2. Clone & Navigate
```bash
cd /project_folder
```

### 3. Run Everything
```bash
./start.sh
```

This will:
- Install backend dependencies
- Start FastAPI backend on http://localhost:8000
- Install frontend dependencies
- Start React frontend on http://localhost:5173

Wait ~10 seconds, then open http://localhost:5173 in your browser.

---

## Manual Setup

### Backend Only

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env (or leave defaults for STUB mode)
cp .env.example .env

# Run backend
cd backend
python app.py
```

Backend will be at: **http://localhost:8000**
API Docs: **http://localhost:8000/docs** (Swagger UI)

### Frontend Only

```bash
cd ui
npm install
npm run dev
```

Frontend will be at: **http://localhost:5173**

---

## Usage

### Upload & Test Documents

1. **Open UI:** http://localhost:5173
2. **Upload Invoice:** Select a JPG/PNG invoice image
3. **Upload Contract:** Select a JSON SOW file (or PDF)
4. **Click "Parse & Extract"** → Extraction will appear
5. **Click "Run Reconciliation"** → Findings will appear
6. **Click "Draft Exception Note"** → Note will be generated
7. **Click "Copy to Clipboard"** → Note copied!




