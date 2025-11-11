"""
Client wrapper for LandingAI's document extraction API
"""

import json
import logging
import requests
import base64
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from models import Invoice, Contract, ExtractionMeta, Box, ParseResult

logger = logging.getLogger(__name__)


@dataclass
class ExtractResult:
    document: Dict[str, Any]
    meta: List[ExtractionMeta]
    parse: ParseResult


class ADEClient:
    
    def __init__(self, api_key: str, mode: str = "ADE"):
        self.api_key = api_key
        self.mode = mode
        self.base_url = "https://api.va.landing.ai/v1/tools"
        self.extract_endpoint = f"{self.base_url}/agentic-document-analysis"
    
    def parse(self, file_path: str) -> ParseResult:
        if self.mode == "STUB":
            return self._parse_stub(file_path)
        else:
            return self._parse_ade(file_path)
    
    def extract(self, file_path: str, schema: Dict[str, Any], doc_type: str = "invoice") -> ExtractResult:
        if self.mode == "STUB":
            return self._extract_stub(file_path, schema, doc_type)
        else:
            return self._extract_ade(file_path, schema, doc_type)
    
    def _parse_stub(self, file_path: str) -> ParseResult:
        logger.info(f"[STUB] Parsing {file_path}")
        return ParseResult(
            pages=1,
            markdown="# Document Content\nMocked markdown from document."
        )
    
    def _parse_ade(self, file_path: str) -> ParseResult:
        logger.info(f"[ADE] Parsing {file_path}")
        
        try:
            result = self._extract_ade(file_path, {}, "document")
            return result.parse
        except Exception as e:
            logger.error(f"[ADE] Parse failed: {e}")
            return ParseResult(pages=1, markdown="# Document Content")
    
    def _extract_stub(
        self,
        file_path: str,
        schema: Dict[str, Any],
        doc_type: str
    ) -> ExtractResult:
        logger.info(f"[STUB] Extracting {doc_type} from {file_path}")
        
        if doc_type == "invoice":
            document = {
                "client_name": "Sample Client Inc",
                "client_address": "123 Main St",
                "seller_name": "Sample Vendor LLC",
                "seller_address": "456 Oak Ave",
                "invoice_number": "INV-001",
                "invoice_date": "01/15/2025",
                "due_date": "02/15/2025",
                "items": [
                    {
                        "description": "Consulting services - Q1 2025",
                        "quantity": 40.0,
                        "unit_price": 150.0,
                        "total_price": 6000.0
                    }
                ],
                "subtotal": {
                    "tax": 600.0,
                    "discount": None,
                    "total": 6600.0
                },
                "currency": "USD",
                "net_terms": "Net 30"
            }
        else:
            document = {
                "vendor_name": "Sample Vendor LLC",
                "client_name": "Sample Client Inc",
                "contract_id": "SOW-001",
                "currency": "USD",
                "net_terms": "Net 30",
                "early_payment_discount": None,
                "default_tax_rate": 0.10,
                "allowed_variance_pct": 2.0,
                "line_items": [
                    {
                        "description": "Consulting services - Q1 2025",
                        "sku": None,
                        "unit_price": 150.0,
                        "max_quantity": 50.0,
                        "discount_pct": None
                    }
                ]
            }
        
        meta = self._create_stub_meta(doc_type)
        
        return ExtractResult(
            document=document,
            meta=meta,
            parse=ParseResult(pages=1)
        )
    
    def _extract_ade(
        self,
        file_path: str,
        schema: Dict[str, Any],
        doc_type: str
    ) -> ExtractResult:
        logger.info(f"[ADE] Extracting {doc_type} from {file_path} with schema")
        
        try:
            import os
            from PIL import Image
            import io
            
            _, ext = os.path.splitext(file_path)
            
            if ext.lower() in ['.jpg', '.jpeg', '.png']:
                logger.info(f"[ADE] Converting image {ext} to PDF")
                img = Image.open(file_path)
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                
                pdf_bytes = io.BytesIO()
                img.save(pdf_bytes, format='PDF')
                file_content = pdf_bytes.getvalue()
                mime_type = 'application/pdf'
                actual_ext = '.pdf'
                logger.info(f"[ADE] Image converted to PDF ({len(file_content)} bytes)")
            else:
                with open(file_path, "rb") as f:
                    file_content = f.read()
                mime_type = 'application/pdf'
                actual_ext = ext
            
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            if schema and schema.get("properties"):
                fields_schema = schema
            else:
                fields_schema = {
                    "type": "object",
                    "properties": {
                        "invoice_number": {"type": "string", "description": "Invoice number"},
                        "issue_date": {"type": "string", "description": "Invoice date"},
                        "seller_name": {"type": "string", "description": "Vendor/Seller name"},
                        "seller_address": {"type": "string", "description": "Seller address"},
                        "seller_tax_id": {"type": "string", "description": "Seller tax ID"},
                        "client_name": {"type": "string", "description": "Client/Buyer name"},
                        "client_address": {"type": "string", "description": "Client address"},
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "no": {"type": "string"},
                                    "description": {"type": "string", "description": "Item description"},
                                    "qty": {"type": "number", "description": "Quantity"},
                                    "net_price": {"type": "number", "description": "Unit price (before tax)"},
                                    "net_worth": {"type": "number", "description": "Line subtotal (before tax)"},
                                    "vat_percent": {"type": "number", "description": "VAT/tax percentage"},
                                    "gross_worth": {"type": "number", "description": "Line total (after tax) - THIS IS REQUIRED"}
                                }
                            },
                            "description": "Line items"
                        },
                        "summary": {
                            "type": "object",
                            "properties": {
                                "net_worth": {"type": "number", "description": "Subtotal before tax"},
                                "vat_value": {"type": "number", "description": "Total tax amount"},
                                "gross_worth": {"type": "number", "description": "Grand total (after tax) - THIS IS REQUIRED"}
                            },
                            "description": "Summary totals"
                        }
                    }
                }
            
            files_data = {
                'pdf': ('document.pdf', file_content, mime_type)
            }
            data = {
                'fields_schema': json.dumps(fields_schema)
            }
            
            logger.info(f"[ADE] File type: {mime_type}, sending as PDF")
            
            logger.info(f"[ADE] Calling LandingAI endpoint: {self.extract_endpoint}")
            
            response = requests.post(
                self.extract_endpoint,
                headers=headers,
                files=files_data,
                data=data,
                timeout=120
            )
            
            response.raise_for_status()
            api_response = response.json()
            
            logger.info(f"[ADE] API Response received")
            
            extracted_data = api_response.get("data", {}).get("extracted_schema", {})
            
            logger.info(f"[ADE] Extract successful for {doc_type}")
            logger.info(f"[ADE] Extracted data keys: {list(extracted_data.keys())}")
            
            cleaned_data = {}
            for key, value in extracted_data.items():
                if isinstance(value, dict) and 'value' in value:
                    cleaned_data[key] = value['value']
                else:
                    cleaned_data[key] = value
            
            logger.info(f"[ADE] Raw cleaned data: {cleaned_data}")
            
            mapped_data = self._map_landing_ai_response(cleaned_data, doc_type)
            
            document = mapped_data if mapped_data else {}
            meta = []
            parse_result = ParseResult(
                pages=1,
                markdown=json.dumps(mapped_data) if mapped_data else ""
            )
            
            logger.info(f"[ADE] Mapped data: {json.dumps(mapped_data, indent=2)[:500]}")
            
            return ExtractResult(
                document=document,
                meta=meta,
                parse=parse_result
            )
        except Exception as e:
            logger.error(f"[ADE] Extract API call failed: {e}")
            logger.error(f"[ADE] Response: {response.text if 'response' in locals() else 'No response'}")
            logger.info(f"[ADE] Falling back to sample data for {doc_type}")
            return self._extract_stub(file_path, schema, doc_type)
    
    def _map_landing_ai_response(self, data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        try:
            mapped = {}
            
            mapped['invoice_number'] = data.get('invoice_number', '')
            mapped['invoice_date'] = data.get('issue_date', '')
            mapped['seller_name'] = data.get('seller_name', '')
            mapped['seller_address'] = data.get('seller_address', '')
            mapped['client_name'] = data.get('client_name', '')
            mapped['client_address'] = data.get('client_address', '')
            
            items = []
            if isinstance(data.get('items'), list):
                for item in data['items']:
                    if isinstance(item, dict) and item:
                        mapped_item = {
                            'description': item.get('description', ''),
                            'quantity': float(item.get('qty', 0)) if item.get('qty') else 0.0,
                            'unit_price': float(item.get('net_price', 0)) if item.get('net_price') else None,
                            'total_price': float(item.get('gross_worth', 0)) if item.get('gross_worth') else 0.0,
                            'tax': None,
                            'sku': None,
                        }
                        items.append(mapped_item)
            
            mapped['items'] = items if items else []
            
            summary = data.get('summary', {})
            if isinstance(summary, dict):
                mapped['subtotal'] = {
                    'tax': float(summary.get('vat_value', 0)) if summary.get('vat_value') else None,
                    'discount': None,
                    'total': float(summary.get('gross_worth', 0)) if summary.get('gross_worth') else 0.0,
                }
            else:
                mapped['subtotal'] = {'tax': None, 'discount': None, 'total': 0.0}
            
            mapped['currency'] = 'USD'
            mapped['net_terms'] = 'Net 30'
            mapped['tax_rate'] = None
            mapped['due_date'] = None
            
            logger.info(f"[ADE] Field mapping complete - {len(mapped.get('items', []))} items")
            
            return mapped
            
        except Exception as e:
            logger.error(f"[ADE] Field mapping failed: {e}")
            return data
    
    def _parse_extraction_meta(self, meta_list: List[Dict[str, Any]]) -> List[ExtractionMeta]:
        result = []
        for item in meta_list:
            try:
                boxes = []
                for box_data in item.get("boxes", []):
                    boxes.append(Box(
                        page=box_data.get("page", 0),
                        left=box_data.get("left", 0),
                        top=box_data.get("top", 0),
                        right=box_data.get("right", 1),
                        bottom=box_data.get("bottom", 1)
                    ))
                
                result.append(ExtractionMeta(
                    field_path=item.get("field_path", ""),
                    boxes=boxes,
                    page=item.get("page", 0)
                ))
            except Exception as e:
                logger.warning(f"Failed to parse metadata item: {e}")
        
        return result
    
    def _create_stub_meta(self, doc_type: str) -> List[ExtractionMeta]:
        if doc_type == "invoice":
            return [
                ExtractionMeta(
                    field_path="client_name",
                    boxes=[Box(page=0, left=0.05, top=0.05, right=0.35, bottom=0.10)],
                    page=0
                ),
                ExtractionMeta(
                    field_path="invoice_number",
                    boxes=[Box(page=0, left=0.65, top=0.05, right=0.95, bottom=0.10)],
                    page=0
                ),
                ExtractionMeta(
                    field_path="items[0].description",
                    boxes=[Box(page=0, left=0.05, top=0.30, right=0.70, bottom=0.38)],
                    page=0
                ),
                ExtractionMeta(
                    field_path="items[0].quantity",
                    boxes=[Box(page=0, left=0.70, top=0.30, right=0.80, bottom=0.38)],
                    page=0
                ),
                ExtractionMeta(
                    field_path="items[0].unit_price",
                    boxes=[Box(page=0, left=0.80, top=0.30, right=0.90, bottom=0.38)],
                    page=0
                ),
                ExtractionMeta(
                    field_path="subtotal.total",
                    boxes=[Box(page=0, left=0.75, top=0.85, right=0.95, bottom=0.92)],
                    page=0
                ),
            ]
        else:
            return [
                ExtractionMeta(
                    field_path="vendor_name",
                    boxes=[Box(page=0, left=0.05, top=0.05, right=0.35, bottom=0.10)],
                    page=0
                ),
                ExtractionMeta(
                    field_path="line_items[0].description",
                    boxes=[Box(page=0, left=0.05, top=0.25, right=0.70, bottom=0.33)],
                    page=0
                ),
                ExtractionMeta(
                    field_path="line_items[0].unit_price",
                    boxes=[Box(page=0, left=0.80, top=0.25, right=0.95, bottom=0.33)],
                    page=0
                ),
            ]

