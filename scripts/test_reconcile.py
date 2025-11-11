"""
Test reconciliation with sample invoice/SOW pairs.
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import Invoice, Contract
from backend.reconcile import ReconcileEngine


def load_sample_data():
    """Load sample invoice and contracts."""
    
    # Sample invoice 1
    invoice1_data = {
        "client_name": "Clark-Foster",
        "seller_name": "Nguyen-Roach",
        "invoice_number": "84652373",
        "invoice_date": "02/23/2021",
        "items": [
            {
                "description": "Stemware Rack Display Kitchen Wine Glass Holder Bottle Carbon Steel Free Punch",
                "quantity": 1.0,
                "unit_price": 46.55,
                "total_price": 46.55,
            },
            {
                "description": "VTG (4) 7 Ounce Since 1852 Milk Bottle Wine Carafe Juice Glass with Cork Lids",
                "quantity": 1.0,
                "unit_price": 15.40,
                "total_price": 15.40,
            },
            {
                "description": "Vintage Crystal Red Wine Glasses NOS West Germany 1983 6 10 ounce elegant stems",
                "quantity": 1.0,
                "unit_price": 39.00,
                "total_price": 39.00,
            },
            {
                "description": "3 Ikea Stainless Steel 4-bottle Wine Rack 300.557.60 - great condition gift it!",
                "quantity": 4.0,
                "unit_price": 27.50,
                "total_price": 110.00,
            },
            {
                "description": "Lolita \"Wine Bouquet\" Hand Painted and Decorated Wine Glass NIB",
                "quantity": 1.0,
                "unit_price": 22.00,
                "total_price": 22.00,
            },
        ],
        "subtotal": {"tax": 21.18, "total": 232.95},
        "currency": "USD",
        "net_terms": "Net 30",
    }
    
    # Load contract SOW
    sow_path = Path("data/contracts/sample_sow_1.json")
    with open(sow_path, "r") as f:
        sow_data = json.load(f)
    
    return Invoice(**invoice1_data), Contract(**sow_data)


def test_perfect_match():
    """Test invoice that matches contract perfectly."""
    print("=" * 80)
    print("TEST 1: Perfect Match (No findings expected)")
    print("=" * 80)
    
    invoice, contract = load_sample_data()
    engine = ReconcileEngine(fuzzy_threshold=85, allowed_variance_pct=2.0)
    
    result = engine.reconcile(invoice, contract)
    
    print(f"Invoice: {invoice.invoice_number} ({invoice.seller_name})")
    print(f"Contract: {contract.contract_id}")
    print(f"\nResults:")
    print(f"  Pass: {result.summary.pass_}")
    print(f"  Major findings: {result.summary.major_count}")
    print(f"  Minor findings: {result.summary.minor_count}")
    print(f"  Total findings: {result.summary.total_count}")
    
    if result.findings:
        print(f"\nFindings:")
        for i, finding in enumerate(result.findings, 1):
            print(f"  {i}. {finding.type} ({finding.severity})")
            print(f"     {finding.details}")
    
    print()
    return result.summary.pass_ and result.summary.total_count == 0


def test_price_variance():
    """Test invoice with price variance."""
    print("=" * 80)
    print("TEST 2: Price Variance (Major finding expected)")
    print("=" * 80)
    
    invoice, contract = load_sample_data()
    
    # Modify invoice line 0 to have different price
    invoice.items[0].unit_price = 50.0  # vs contract 46.55 = 7.4% variance > 2%
    
    engine = ReconcileEngine(fuzzy_threshold=85, allowed_variance_pct=2.0)
    result = engine.reconcile(invoice, contract)
    
    print(f"Invoice: {invoice.invoice_number}")
    print(f"  Line 0 unit price: ${invoice.items[0].unit_price}")
    print(f"  Contract unit price: ${contract.line_items[0].unit_price}")
    
    print(f"\nResults:")
    print(f"  Pass: {result.summary.pass_}")
    print(f"  Major findings: {result.summary.major_count}")
    print(f"  Minor findings: {result.summary.minor_count}")
    
    if result.findings:
        print(f"\nFindings:")
        for i, finding in enumerate(result.findings, 1):
            print(f"  {i}. {finding.type} ({finding.severity})")
            print(f"     {finding.details}")
    
    print()
    
    # Check for price variance finding
    has_price_variance = any(f.type == "UNIT_PRICE_VARIANCE" for f in result.findings)
    return has_price_variance and result.summary.major_count > 0


def test_unknown_line():
    """Test invoice with extra line not in contract."""
    print("=" * 80)
    print("TEST 3: Unknown Line (Major finding expected)")
    print("=" * 80)
    
    invoice, contract = load_sample_data()
    
    # Add extra line to invoice
    from backend.models import InvoiceLine
    invoice.items.append(InvoiceLine(
        description="Extra service not in contract",
        quantity=1.0,
        unit_price=100.0,
        total_price=100.0,
    ))
    
    engine = ReconcileEngine(fuzzy_threshold=85, allowed_variance_pct=2.0)
    result = engine.reconcile(invoice, contract)
    
    print(f"Invoice: {invoice.invoice_number}")
    print(f"  Total lines: {len(invoice.items)}")
    print(f"  Contract lines: {len(contract.line_items)}")
    
    print(f"\nResults:")
    print(f"  Pass: {result.summary.pass_}")
    print(f"  Major findings: {result.summary.major_count}")
    
    if result.findings:
        print(f"\nFindings:")
        for i, finding in enumerate(result.findings, 1):
            print(f"  {i}. {finding.type} ({finding.severity})")
            print(f"     {finding.details}")
    
    print()
    
    # Check for unknown line finding
    has_unknown_line = any(f.type == "UNKNOWN_LINE" for f in result.findings)
    return has_unknown_line and result.summary.major_count > 0


def test_currency_mismatch():
    """Test invoice with different currency."""
    print("=" * 80)
    print("TEST 4: Currency Mismatch (Major finding expected)")
    print("=" * 80)
    
    invoice, contract = load_sample_data()
    invoice.currency = "EUR"  # vs contract USD
    
    engine = ReconcileEngine(fuzzy_threshold=85, allowed_variance_pct=2.0)
    result = engine.reconcile(invoice, contract)
    
    print(f"Invoice currency: {invoice.currency}")
    print(f"Contract currency: {contract.currency}")
    
    print(f"\nResults:")
    print(f"  Pass: {result.summary.pass_}")
    print(f"  Major findings: {result.summary.major_count}")
    
    if result.findings:
        print(f"\nFindings:")
        for i, finding in enumerate(result.findings, 1):
            print(f"  {i}. {finding.type} ({finding.severity})")
            print(f"     {finding.details}")
    
    print()
    
    has_currency_mismatch = any(f.type == "CURRENCY_MISMATCH" for f in result.findings)
    return has_currency_mismatch and result.summary.major_count > 0


def test_terms_mismatch():
    """Test invoice with different net terms."""
    print("=" * 80)
    print("TEST 5: Terms Mismatch (Minor finding expected)")
    print("=" * 80)
    
    invoice, contract = load_sample_data()
    invoice.net_terms = "Net 60"  # vs contract Net 30
    
    engine = ReconcileEngine(fuzzy_threshold=85, allowed_variance_pct=2.0)
    result = engine.reconcile(invoice, contract)
    
    print(f"Invoice terms: {invoice.net_terms}")
    print(f"Contract terms: {contract.net_terms}")
    
    print(f"\nResults:")
    print(f"  Pass: {result.summary.pass_}")
    print(f"  Major findings: {result.summary.major_count}")
    print(f"  Minor findings: {result.summary.minor_count}")
    
    if result.findings:
        print(f"\nFindings:")
        for i, finding in enumerate(result.findings, 1):
            print(f"  {i}. {finding.type} ({finding.severity})")
            print(f"     {finding.details}")
    
    print()
    
    has_terms_mismatch = any(f.type == "TERMS_MISMATCH" for f in result.findings)
    return has_terms_mismatch and result.summary.minor_count > 0


if __name__ == "__main__":
    print("\n🧪 PactProof Reconciliation Tests\n")
    
    tests = [
        ("Perfect Match", test_perfect_match),
        ("Price Variance", test_price_variance),
        ("Unknown Line", test_unknown_line),
        ("Currency Mismatch", test_currency_mismatch),
        ("Terms Mismatch", test_terms_mismatch),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ {name} failed with error: {e}\n")
            results.append((name, False))
    
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} passed")

