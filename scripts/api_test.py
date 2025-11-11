"""
Quick API Testing Script
Tests all endpoints with sample data
"""

import json
import requests
import time

API_BASE = "http://localhost:8000"

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def test_health():
    """Test health endpoint."""
    print(f"\n{BLUE}→ Testing /health{RESET}")
    try:
        resp = requests.get(f"{API_BASE}/health")
        resp.raise_for_status()
        print(f"  {GREEN}✅ Status: {resp.json()['status']}{RESET}")
        return True
    except Exception as e:
        print(f"  {RED}❌ Error: {e}{RESET}")
        return False


def test_parse_extract_invoice():
    """Test invoice extraction."""
    print(f"\n{BLUE}→ Testing /parse_extract/invoice{RESET}")
    try:
        # Create a dummy file
        files = {"file": ("test.jpg", b"fake image data")}
        resp = requests.post(
            f"{API_BASE}/parse_extract/invoice",
            files=files,
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("invoice"):
            invoice = data["invoice"]
            print(f"  {GREEN}✅ Extracted invoice{RESET}")
            print(f"     Vendor: {invoice.get('seller_name')}")
            print(f"     Invoice #: {invoice.get('invoice_number')}")
            print(f"     Total: ${invoice.get('subtotal', {}).get('total', 0):.2f}")
            print(f"     Lines: {len(invoice.get('items', []))}")
            return True
        else:
            print(f"  {RED}❌ No invoice in response{RESET}")
            return False
    except Exception as e:
        print(f"  {RED}❌ Error: {e}{RESET}")
        return False


def test_parse_extract_contract():
    """Test contract extraction."""
    print(f"\n{BLUE}→ Testing /parse_extract/contract{RESET}")
    try:
        # Load sample SOW
        with open("data/contracts/sample_sow_1.json", "r") as f:
            contract_data = json.load(f)
        
        files = {"file": ("contract.json", json.dumps(contract_data).encode())}
        resp = requests.post(
            f"{API_BASE}/parse_extract/contract",
            files=files,
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("contract"):
            contract = data["contract"]
            print(f"  {GREEN}✅ Extracted contract{RESET}")
            print(f"     Vendor: {contract.get('vendor_name')}")
            print(f"     Contract ID: {contract.get('contract_id')}")
            print(f"     Lines: {len(contract.get('line_items', []))}")
            return True
        else:
            print(f"  {RED}❌ No contract in response{RESET}")
            return False
    except Exception as e:
        print(f"  {RED}❌ Error: {e}{RESET}")
        return False


def test_reconcile():
    """Test reconciliation endpoint."""
    print(f"\n{BLUE}→ Testing /reconcile{RESET}")
    try:
        # First extract
        files_invoice = {"file": ("test.jpg", b"fake image data")}
        inv_resp = requests.post(
            f"{API_BASE}/parse_extract/invoice",
            files=files_invoice,
            timeout=10
        )
        inv_resp.raise_for_status()
        invoice = inv_resp.json().get("invoice")
        
        # Load sample contract
        with open("data/contracts/sample_sow_1.json", "r") as f:
            contract_data = json.load(f)
        
        files_contract = {"file": ("contract.json", json.dumps(contract_data).encode())}
        cont_resp = requests.post(
            f"{API_BASE}/parse_extract/contract",
            files=files_contract,
            timeout=10
        )
        cont_resp.raise_for_status()
        contract = cont_resp.json().get("contract")
        
        # Reconcile
        payload = {
            "invoice": invoice,
            "contract": contract
        }
        resp = requests.post(
            f"{API_BASE}/reconcile",
            json=payload,
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        summary = result.get("summary", {})
        findings = result.get("findings", [])
        
        print(f"  {GREEN}✅ Reconciliation complete{RESET}")
        print(f"     Status: {'✅ PASSED' if summary.get('pass') else '❌ FAILED'}")
        print(f"     Major: {summary.get('major_count')} | Minor: {summary.get('minor_count')}")
        print(f"     Findings: {len(findings)}")
        
        if findings:
            print(f"\n     {BLUE}Findings:{RESET}")
            for i, finding in enumerate(findings[:3], 1):
                print(f"       {i}. {finding['type']} ({finding['severity']})")
                print(f"          {finding['details'][:60]}...")
        
        return True
    except Exception as e:
        print(f"  {RED}❌ Error: {e}{RESET}")
        return False


def test_draft_note():
    """Test note generation endpoint."""
    print(f"\n{BLUE}→ Testing /draft_note{RESET}")
    try:
        # Extract
        files_invoice = {"file": ("test.jpg", b"fake image data")}
        inv_resp = requests.post(
            f"{API_BASE}/parse_extract/invoice",
            files=files_invoice,
            timeout=10
        )
        inv_resp.raise_for_status()
        invoice = inv_resp.json().get("invoice")
        
        with open("data/contracts/sample_sow_1.json", "r") as f:
            contract_data = json.load(f)
        
        files_contract = {"file": ("contract.json", json.dumps(contract_data).encode())}
        cont_resp = requests.post(
            f"{API_BASE}/parse_extract/contract",
            files=files_contract,
            timeout=10
        )
        cont_resp.raise_for_status()
        contract = cont_resp.json().get("contract")
        
        # Reconcile
        recon_payload = {
            "invoice": invoice,
            "contract": contract
        }
        recon_resp = requests.post(
            f"{API_BASE}/reconcile",
            json=recon_payload,
            timeout=10
        )
        recon_resp.raise_for_status()
        reconcile = recon_resp.json()
        
        # Draft note
        payload = {
            "invoice": invoice,
            "contract": contract,
            "reconcile": reconcile
        }
        resp = requests.post(
            f"{API_BASE}/draft_note",
            json=payload,
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        markdown = result.get("markdown", "")
        if markdown:
            print(f"  {GREEN}✅ Note generated{RESET}")
            print(f"     Length: {len(markdown)} chars")
            print(f"\n     {BLUE}Preview (first 300 chars):{RESET}")
            for line in markdown[:300].split("\n")[:5]:
                print(f"     {line}")
            print(f"     ...")
            return True
        else:
            print(f"  {RED}❌ No markdown in response{RESET}")
            return False
    except Exception as e:
        print(f"  {RED}❌ Error: {e}{RESET}")
        return False


def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  PactProof API Test Suite{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    print(f"\n{BLUE}Connecting to {API_BASE}...{RESET}")
    
    tests = [
        ("Health Check", test_health),
        ("Parse Invoice", test_parse_extract_invoice),
        ("Parse Contract", test_parse_extract_contract),
        ("Reconciliation", test_reconcile),
        ("Draft Note", test_draft_note),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except KeyboardInterrupt:
            print(f"\n{RED}Interrupted!{RESET}")
            break
        except Exception as e:
            print(f"  {RED}❌ Unexpected error: {e}{RESET}")
            results.append((name, False))
        
        time.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    for name, passed in results:
        status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
        print(f"{status}: {name}")
    
    print(f"\n{BLUE}Total: {passed_count}/{total_count} passed{RESET}")
    
    if passed_count == total_count:
        print(f"\n{GREEN}🎉 All tests passed!{RESET}\n")
        return 0
    else:
        print(f"\n{RED}⚠️  Some tests failed.{RESET}\n")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

