"""
Pydantic models for the application
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class FindingSeverity(str, Enum):
    MAJOR = "MAJOR"
    MINOR = "MINOR"


class FindingType(str, Enum):
    UNIT_PRICE_VARIANCE = "UNIT_PRICE_VARIANCE"
    QUANTITY_OVERFLOW = "QUANTITY_OVERFLOW"
    UNKNOWN_LINE = "UNKNOWN_LINE"
    CURRENCY_MISMATCH = "CURRENCY_MISMATCH"
    TERMS_MISMATCH = "TERMS_MISMATCH"
    TAX_MISMATCH = "TAX_MISMATCH"


class Box(BaseModel):
    page: int = Field(default=0, description="Page number (0-indexed)")
    left: float = Field(ge=0, le=1, description="Left coordinate [0..1]")
    top: float = Field(ge=0, le=1, description="Top coordinate [0..1]")
    right: float = Field(ge=0, le=1, description="Right coordinate [0..1]")
    bottom: float = Field(ge=0, le=1, description="Bottom coordinate [0..1]")


class ExtractionMeta(BaseModel):
    field_path: str = Field(description="Path to field in extracted JSON")
    boxes: List[Box] = Field(default_factory=list, description="Bounding boxes")
    page: Optional[int] = Field(default=0, description="Primary page")


class InvoiceLine(BaseModel):
    description: str
    quantity: float
    unit_price: Optional[float] = None
    total_price: float
    tax: Optional[float] = None
    sku: Optional[str] = None


class Invoice(BaseModel):
    client_name: str
    client_address: Optional[str] = None
    seller_name: str
    seller_address: Optional[str] = None
    invoice_number: str
    invoice_date: str
    due_date: Optional[str] = None
    items: List[InvoiceLine]
    subtotal: Dict[str, Any]
    currency: str = Field(default="USD")
    net_terms: Optional[str] = Field(default="Net 30")
    tax_rate: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "client_name": "Clark-Foster",
                "seller_name": "Nguyen-Roach",
                "invoice_number": "84652373",
                "invoice_date": "02/23/2021",
                "items": [
                    {
                        "description": "Stemware Rack Display Kitchen",
                        "quantity": 1.0,
                        "total_price": 46.55,
                    }
                ],
                "subtotal": {"tax": 21.18, "total": 232.95},
                "currency": "USD",
                "net_terms": "Net 30",
            }
        }


class ContractLine(BaseModel):
    description: str
    sku: Optional[str] = None
    unit_price: float
    max_quantity: Optional[float] = None
    discount_pct: Optional[float] = None
    tax_rate: Optional[float] = None


class Contract(BaseModel):
    vendor_name: str
    client_name: str
    contract_id: str
    currency: str = Field(default="USD")
    net_terms: str = Field(default="Net 30")
    early_payment_discount: Optional[float] = None
    default_tax_rate: float = Field(default=0.0909)
    allowed_variance_pct: float = Field(default=2.0)
    line_items: List[ContractLine]

    class Config:
        json_schema_extra = {
            "example": {
                "vendor_name": "Nguyen-Roach",
                "client_name": "Clark-Foster",
                "contract_id": "SOW-84652373",
                "currency": "USD",
                "net_terms": "Net 30",
                "default_tax_rate": 0.0909,
                "allowed_variance_pct": 2.0,
                "line_items": [
                    {
                        "description": "Stemware Rack Display Kitchen Wine Glass Holder",
                        "unit_price": 46.55,
                        "max_quantity": None,
                    }
                ],
            }
        }


class Finding(BaseModel):
    type: FindingType
    severity: FindingSeverity
    details: str
    invoice_line_idx: Optional[int] = None
    contract_line_idx: Optional[int] = None
    evidence_page: Optional[int] = None
    evidence_boxes: List[Box] = Field(default_factory=list)


class ReconcileSummary(BaseModel):
    pass_: bool = Field(alias="pass")
    major_count: int
    minor_count: int
    total_count: int


class ReconcileResponse(BaseModel):
    summary: ReconcileSummary
    findings: List[Finding]

    class Config:
        populate_by_name = True


class ParseResult(BaseModel):
    pages: int
    markdown: Optional[str] = None


class ExtractionResponse(BaseModel):
    invoice: Optional[Invoice] = None
    contract: Optional[Contract] = None
    meta: List[ExtractionMeta]
    parse: ParseResult
    file_url: str
    file_path: str


class NoteGenerationRequest(BaseModel):
    invoice: Invoice
    contract: Contract
    reconcile: ReconcileResponse


class NoteGenerationResponse(BaseModel):
    markdown: str
    html: Optional[str] = None

