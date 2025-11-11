# PactProof Setup Guide

## ⚡ Quick Start (2 minutes)

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)
- macOS, Linux, or Windows (WSL)

### 2. Clone & Navigate
```bash
cd /Users/kholla/Library/CloudStorage/OneDrive-RedVentures/Code/hackathon2025/landingAI
```

### 3. Run Everything
```bash
./start.sh
```

This will:
- ✅ Install backend dependencies
- ✅ Start FastAPI backend on http://localhost:8000
- ✅ Install frontend dependencies
- ✅ Start React frontend on http://localhost:5173

Wait ~20 seconds, then open http://localhost:5173 in your browser.

---

## 🔧 Manual Setup

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

## 📖 Usage

### Upload & Test Documents

1. **Open UI:** http://localhost:5173
2. **Upload Invoice:** Select a JPG/PNG invoice image
3. **Upload Contract:** Select a JSON SOW file (or PDF)
4. **Click "Parse & Extract"** → Extraction will appear
5. **Click "Run Reconciliation"** → Findings will appear
6. **Click "Draft Exception Note"** → Note will be generated
7. **Click "Copy to Clipboard"** → Note copied!

### Test with Sample Data

We've provided 3 sample invoices and corresponding SOWs:

```
data/contracts/sample_sow_1.json   ← For wine glasses invoice
data/contracts/sample_sow_2.json   ← For soccer cleats invoice
data/contracts/sample_sow_3.json   ← For gaming consoles invoice
```

#### Flow 1: Perfect Match (No findings)
1. Upload invoice from `data/invoices/` (any image will work in STUB mode)
2. Upload corresponding SOW from `data/contracts/`
3. Should see: ✅ PASSED, 0 major, 0 minor

#### Flow 2: Challenge Case (Multiple findings)
1. Upload invoice
2. Upload SOW with different unit prices/terms
3. Should see: ❌ FAILED, multiple major/minor findings

---

## 🧪 Testing

### Run Unit Tests
```bash
python scripts/test_reconcile.py
```

Expected output:
```
✅ PASS: Perfect Match
✅ PASS: Price Variance
✅ PASS: Unknown Line
✅ PASS: Currency Mismatch
✅ PASS: Terms Mismatch

Total: 5/5 passed
```

### Test API Endpoints Directly

```bash
# Health check
curl http://localhost:8000/health

# Parse invoice (multipart upload)
curl -X POST \
  -F "file=@/path/to/invoice.jpg" \
  http://localhost:8000/parse_extract/invoice

# Reconcile invoice vs contract
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "invoice": { ... },
    "contract": { ... }
  }' \
  http://localhost:8000/reconcile
```

See **README.md** for full API reference.

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Extraction mode: STUB (mock) or ADE (real)
APP_MODE=STUB

# LandingAI API key (required if APP_MODE=ADE)
VISION_AGENT_API_KEY=your_key_here

# Google Gemini API key (optional, for LLM note enhancement)
GOOGLE_API_KEY=your_key_here

# Frontend API base URL
VITE_API_BASE_URL=http://localhost:8000

# Reconciliation tuning
FUZZY_MATCH_THRESHOLD=85
ALLOWED_VARIANCE_PCT=2.0
```

### STUB Mode (Default)
- No API keys needed
- Uses mock invoice/contract data
- Perfect for development & demos
- All endpoints return realistic responses

### ADE Mode (Real Extraction)
1. Get API key from [LandingAI](https://landing.ai)
2. Set `APP_MODE=ADE`
3. Set `VISION_AGENT_API_KEY=your_key`
4. Restart backend
5. Real ADE extraction will be used

---

## 📁 Project Structure

```
landingAI/
├── backend/                    # Python FastAPI backend
│   ├── app.py                 # Main FastAPI application
│   ├── models.py              # Pydantic data models
│   ├── config.py              # Configuration & settings
│   ├── ade_client.py           # LandingAI ADE wrapper
│   ├── reconcile.py           # Reconciliation logic
│   └── note.py                # Exception note generation
│
├── ui/                        # React+TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── UploadPane.tsx
│   │   │   ├── DocViewer.tsx
│   │   │   ├── ExtractionPane.tsx
│   │   │   ├── FindingsPane.tsx
│   │   │   └── NoteDisplay.tsx
│   │   ├── api/
│   │   │   └── client.ts      # API client
│   │   ├── store/
│   │   │   └── appStore.ts    # Zustand state
│   │   ├── types/
│   │   │   └── api.ts         # TypeScript interfaces
│   │   ├── styles/            # CSS stylesheets
│   │   ├── App.tsx            # Main App component
│   │   └── main.tsx           # Entry point
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── schemas/                   # JSON Schemas for ADE
│   ├── invoice.schema.json
│   └── contract.schema.json
│
├── data/
│   ├── invoices/              # Sample invoice images
│   └── contracts/             # Sample SOW JSON files
│       ├── sample_sow_1.json
│       ├── sample_sow_2.json
│       └── sample_sow_3.json
│
├── scripts/
│   ├── test_reconcile.py      # Unit tests
│   └── api_test.py            # API endpoint tests
│
├── requirements.txt           # Python dependencies
├── README.md                  # Main documentation
├── SETUP.md                   # This file
├── start.sh                   # Quick start script
├── .env.example               # Environment template
├── .gitignore
└── LICENSE
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Make sure port 8000 is free
lsof -i :8000

# Or use different port
PYTHONPATH=. uvicorn backend.app:app --port 8001
```

### Frontend won't start
```bash
# Clear node_modules and reinstall
cd ui
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### API returns 500 errors
1. Check backend logs for errors
2. Ensure `.env` file is present
3. Verify Python version: `python --version` (should be 3.10+)
4. Check file permissions on `uploads/` and `out/extracted/`

### Tests fail
```bash
# Reinstall dependencies
pip install -q --upgrade -r requirements.txt

# Run tests with verbose output
python -u scripts/test_reconcile.py
```

### Can't upload files
1. The `uploads/` directory will be auto-created on startup
2. Check file size < 50MB
3. Try different file format (JPG/PNG for invoices, JSON for contracts)

---

## 🚀 Production Deployment

### Docker

```bash
docker build -t pactproof .
docker run -p 8000:8000 -p 5173:5173 pactproof
```

(Dockerfile coming soon)

### Cloud

Deploy to:
- **Backend:** Heroku, Railway, Render, Google Cloud Run
- **Frontend:** Vercel, Netlify, AWS S3 + CloudFront

---

## 📞 Support

- **Issues?** Check this file or README.md
- **API Questions?** Visit http://localhost:8000/docs
- **Code Issues?** Check backend logs: `tail -f backend.log`

---

## ✅ Success Checklist

- [ ] `./start.sh` runs without errors
- [ ] Backend health: http://localhost:8000/health returns `{"status":"ok"}`
- [ ] Frontend loads: http://localhost:5173 shows PactProof UI
- [ ] Tests pass: `python scripts/test_reconcile.py` shows 5/5 ✅
- [ ] Can upload files and see extraction
- [ ] Can run reconciliation and see findings
- [ ] Can draft and copy exception notes

---

**Happy testing! 🎉**

