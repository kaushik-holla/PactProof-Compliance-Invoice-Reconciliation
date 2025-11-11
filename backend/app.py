"""
FastAPI backend for PactProof - handles invoice reconciliation
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
import shutil
import io
from datetime import datetime

from config import get_settings
from models import (
    Invoice,
    Contract,
    ReconcileResponse,
    NoteGenerationRequest,
    NoteGenerationResponse,
    ExtractionResponse,
)
from ade_client import ADEClient
from reconcile import ReconcileEngine
from note import NoteGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()

os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs("out/extracted", exist_ok=True)

app = FastAPI(
    title="PactProof API",
    description="Compliance invoice reconciliation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ade_client = ADEClient(
    api_key=settings.vision_agent_api_key,
    mode=settings.app_mode
)
reconcile_engine = ReconcileEngine(
    fuzzy_threshold=settings.fuzzy_match_threshold,
    allowed_variance_pct=settings.allowed_variance_pct
)
note_generator = NoteGenerator(google_api_key=settings.google_api_key)


def load_schema(schema_name: str) -> dict:
    schema_path = f"schemas/{schema_name}.schema.json"
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            return json.load(f)
    return {}


INVOICE_SCHEMA = load_schema("invoice")
CONTRACT_SCHEMA = load_schema("contract")


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app_mode": settings.app_mode,
        "version": "1.0.0"
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    try:
        if file.size > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File too large (max {settings.max_upload_size_mb}MB)"
            )
        
        file_path = os.path.join(settings.upload_dir, file.filename)
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        file_url = f"{settings.api_origin}/uploads/{file.filename}"
        
        logger.info(f"Uploaded {file.filename} ({len(contents)} bytes)")
        
        return {
            "filename": file.filename,
            "file_url": file_url,
            "size": len(contents)
        }
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/uploads/{filename}")
async def serve_file(filename: str):
    file_path = os.path.join(settings.upload_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.post("/parse_extract/invoice", response_model=ExtractionResponse)
async def parse_extract_invoice(file: UploadFile = File(...)) -> dict:
    try:
        file_path = os.path.join(settings.upload_dir, file.filename)
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        logger.info(f"Parsing invoice from {file.filename}")
        
        parse_result = ade_client.parse(file_path)
        
        extract_result = ade_client.extract(
            file_path,
            schema=INVOICE_SCHEMA,
            doc_type="invoice"
        )
        
        invoice = Invoice(**extract_result.document)
        
        extracted_data = {
            "invoice": invoice.model_dump(),
            "meta": [m.model_dump() for m in extract_result.meta],
            "parse": extract_result.parse.model_dump(),
        }
        
        out_path = f"out/extracted/{file.filename}.json"
        os.makedirs("out/extracted", exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(extracted_data, f, indent=2)
        
        file_url = f"{settings.api_origin}/uploads/{file.filename}"
        
        return {
            "invoice": invoice,
            "contract": None,
            "meta": extract_result.meta,
            "parse": extract_result.parse,
            "file_url": file_url,
            "file_path": file_path,
        }
    
    except Exception as e:
        logger.error(f"Invoice extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse_extract/contract", response_model=ExtractionResponse)
async def parse_extract_contract(file: UploadFile = File(...)) -> dict:
    try:
        file_path = os.path.join(settings.upload_dir, file.filename)
        
        if file.filename.endswith(".json"):
            contents = await file.read()
            contract_data = json.loads(contents)
            
            with open(file_path, "wb") as f:
                f.write(contents)
            
            contract = Contract(**contract_data)
            
            logger.info(f"Loaded contract from JSON: {file.filename}")
            
            meta = []
            
            file_url = f"{settings.api_origin}/uploads/{file.filename}"
            
            return {
                "invoice": None,
                "contract": contract,
                "meta": meta,
                "parse": {"pages": 1},
                "file_url": file_url,
                "file_path": file_path,
            }
        else:
            with open(file_path, "wb") as f:
                contents = await file.read()
                f.write(contents)
            
            parse_result = ade_client.parse(file_path)
            extract_result = ade_client.extract(
                file_path,
                schema=CONTRACT_SCHEMA,
                doc_type="contract"
            )
            
            contract = Contract(**extract_result.document)
            
            logger.info(f"Parsed contract from {file.filename}")
            
            file_url = f"{settings.api_origin}/uploads/{file.filename}"
            
            return {
                "invoice": None,
                "contract": contract,
                "meta": extract_result.meta,
                "parse": extract_result.parse,
                "file_url": file_url,
                "file_path": file_path,
            }
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    except Exception as e:
        logger.error(f"Contract extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reconcile", response_model=ReconcileResponse)
async def reconcile(invoice: Invoice, contract: Contract) -> dict:
    try:
        logger.info(
            f"Reconciling invoice {invoice.invoice_number} "
            f"against contract {contract.contract_id}"
        )
        
        result = reconcile_engine.reconcile(invoice, contract)
        
        logger.info(
            f"Reconciliation complete: {result.summary.total_count} findings "
            f"({result.summary.major_count} major, {result.summary.minor_count} minor)"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Reconciliation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/draft_note", response_model=NoteGenerationResponse)
async def draft_note(request: NoteGenerationRequest) -> dict:
    try:
        logger.info(f"Generating note for invoice {request.invoice.invoice_number}")
        
        markdown = note_generator.draft_note(
            request.invoice,
            request.contract,
            request.reconcile
        )
        
        logger.info("Note generated successfully")
        
        return {
            "markdown": markdown,
            "html": None,
        }
    
    except Exception as e:
        logger.error(f"Note generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export_note_pdf")
async def export_note_pdf(
    note_text: str = Body(..., embed=True),
    invoice_number: Optional[str] = Body(None, embed=True)
):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        from reportlab.pdfgen import canvas
        
        logger.info(f"Generating PDF for note (invoice: {invoice_number})")
        
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor='#1a1a1a',
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        
        pre_style = ParagraphStyle(
            'PreFormatted',
            parent=styles['Code'],
            fontSize=9,
            leading=11,
            leftIndent=0,
            rightIndent=0,
            fontName='Courier',
        )
        
        story.append(Paragraph("COMPLIANCE INVOICE RECONCILIATION REPORT", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        for line in note_text.split('\n'):
            if line.strip():
                story.append(Preformatted(line, pre_style))
            else:
                story.append(Spacer(1, 6))
        
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"compliance_report_{invoice_number or 'note'}_{timestamp}.pdf"
        
        logger.info(f"PDF generated successfully: {filename}")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except ImportError:
        logger.error("ReportLab library not installed")
        raise HTTPException(
            status_code=500,
            detail="PDF generation library not installed. Please install reportlab."
        )
    except Exception as e:
        logger.error(f"PDF export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup():
    logger.info(" PactProof API starting...")
    logger.info(f"   Mode: {settings.app_mode}")
    logger.info(f"   API Origin: {settings.api_origin}")
    logger.info(f"   Upload Dir: {settings.upload_dir}")


@app.on_event("shutdown")
async def shutdown():
    logger.info(" PactProof API shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

