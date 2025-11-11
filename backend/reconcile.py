"""
Reconciliation engine - matches invoices to contracts
"""

import logging
from typing import List, Tuple, Dict, Optional
from rapidfuzz import fuzz
from models import (
    Invoice,
    Contract,
    Finding,
    FindingType,
    FindingSeverity,
    ReconcileResponse,
    ReconcileSummary,
)

logger = logging.getLogger(__name__)


class ReconcileEngine:
    
    def __init__(
        self,
        fuzzy_threshold: int = 85,
        allowed_variance_pct: float = 2.0
    ):
        self.fuzzy_threshold = fuzzy_threshold
        self.allowed_variance_pct = allowed_variance_pct
    
    def reconcile(self, invoice: Invoice, contract: Contract) -> ReconcileResponse:
        findings: List[Finding] = []
        
        findings.extend(self._check_currency(invoice, contract))
        findings.extend(self._check_net_terms(invoice, contract))
        
        line_matches = self._match_lines(invoice, contract)
        findings.extend(self._check_line_variances(invoice, contract, line_matches))
        
        major_findings = [f for f in findings if f.severity == FindingSeverity.MAJOR]
        minor_findings = [f for f in findings if f.severity == FindingSeverity.MINOR]
        passed = len(major_findings) == 0
        
        summary = ReconcileSummary(
            **{
                "pass": passed,
                "major_count": len(major_findings),
                "minor_count": len(minor_findings),
                "total_count": len(findings),
            }
        )
        
        return ReconcileResponse(summary=summary, findings=findings)
    
    def _match_lines(
        self,
        invoice: Invoice,
        contract: Contract
    ) -> List[Tuple[int, int, float]]:
        matches: List[Tuple[int, int, float]] = []
        matched_contract_indices = set()
        
        for inv_idx, inv_line in enumerate(invoice.items):
            best_match = None
            best_confidence = 0.0
            best_contract_idx = -1
            
            for cont_idx, cont_line in enumerate(contract.line_items):
                if cont_idx in matched_contract_indices:
                    continue
                
                confidence = self._line_similarity(inv_line.description, cont_line.description)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = (inv_idx, cont_idx, confidence)
                    best_contract_idx = cont_idx
            
            if best_match and best_confidence >= (self.fuzzy_threshold / 100.0):
                matches.append(best_match)
                matched_contract_indices.add(best_contract_idx)
        
        return matches
    
    def _line_similarity(self, inv_desc: str, cont_desc: str) -> float:
        inv_desc_norm = " ".join(inv_desc.lower().split())
        cont_desc_norm = " ".join(cont_desc.lower().split())
        
        score = fuzz.token_set_ratio(inv_desc_norm, cont_desc_norm)
        return score / 100.0
    
    def _check_currency(self, invoice: Invoice, contract: Contract) -> List[Finding]:
        findings: List[Finding] = []
        
        inv_curr = invoice.currency or "USD"
        cont_curr = contract.currency or "USD"
        
        if inv_curr != cont_curr:
            findings.append(Finding(
                type=FindingType.CURRENCY_MISMATCH,
                severity=FindingSeverity.MAJOR,
                details=f"Currency mismatch: Invoice {inv_curr} vs Contract {cont_curr}",
            ))
        
        return findings
    
    def _check_net_terms(self, invoice: Invoice, contract: Contract) -> List[Finding]:
        findings: List[Finding] = []
        
        inv_terms = invoice.net_terms or "Net 30"
        cont_terms = contract.net_terms or "Net 30"
        
        if inv_terms != cont_terms:
            findings.append(Finding(
                type=FindingType.TERMS_MISMATCH,
                severity=FindingSeverity.MINOR,
                details=f"Net terms mismatch: Invoice {inv_terms} vs Contract {cont_terms}",
            ))
        
        return findings
    
    def _check_line_variances(
        self,
        invoice: Invoice,
        contract: Contract,
        line_matches: List[Tuple[int, int, float]]
    ) -> List[Finding]:
        findings: List[Finding] = []
        matched_inv_indices = {m[0] for m in line_matches}
        matched_cont_indices = {m[1] for m in line_matches}
        
        for inv_idx, cont_idx, _conf in line_matches:
            inv_line = invoice.items[inv_idx]
            cont_line = contract.line_items[cont_idx]
            
            if inv_line.unit_price and cont_line.unit_price:
                variance = self._compute_variance(
                    inv_line.unit_price,
                    cont_line.unit_price
                )
                if variance > (self.allowed_variance_pct / 100.0):
                    findings.append(Finding(
                        type=FindingType.UNIT_PRICE_VARIANCE,
                        severity=FindingSeverity.MAJOR,
                        details=f"Unit price variance {variance*100:.1f}% exceeds {self.allowed_variance_pct}%: "
                                f"Invoice ${inv_line.unit_price:.2f} vs Contract ${cont_line.unit_price:.2f}",
                        invoice_line_idx=inv_idx,
                        contract_line_idx=cont_idx,
                    ))
            
            if cont_line.max_quantity and inv_line.quantity > cont_line.max_quantity:
                findings.append(Finding(
                    type=FindingType.QUANTITY_OVERFLOW,
                    severity=FindingSeverity.MAJOR,
                    details=f"Quantity {inv_line.quantity} exceeds contract max {cont_line.max_quantity}",
                    invoice_line_idx=inv_idx,
                    contract_line_idx=cont_idx,
                ))
        
        for inv_idx in range(len(invoice.items)):
            if inv_idx not in matched_inv_indices:
                inv_line = invoice.items[inv_idx]
                findings.append(Finding(
                    type=FindingType.UNKNOWN_LINE,
                    severity=FindingSeverity.MAJOR,
                    details=f"No matching contract line for invoice item: {inv_line.description[:60]}...",
                    invoice_line_idx=inv_idx,
                ))
        
        return findings
    
    def _compute_variance(self, actual: float, expected: float) -> float:
        if expected == 0:
            return 1.0 if actual != 0 else 0.0
        return abs(actual - expected) / expected

