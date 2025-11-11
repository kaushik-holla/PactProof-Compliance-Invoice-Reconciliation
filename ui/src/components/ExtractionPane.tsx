import React from "react";
import { useAppStore } from "../store/appStore";
import { Invoice, Contract } from "../types/api";
import "../styles/components.css";

export const ExtractionPane: React.FC = () => {
  const { invoice, contract, setHighlightedFieldPath } = useAppStore();

  const renderInvoiceFields = () => {
    if (!invoice) return <div className="placeholder">No invoice extracted</div>;

    return (
      <div className="extraction-section">
        <h4>Invoice Details</h4>
        <table className="fields-table">
          <tbody>
            <tr onMouseEnter={() => setHighlightedFieldPath("seller_name")}>
              <td className="field-label">Vendor:</td>
              <td>{invoice.seller_name}</td>
            </tr>
            <tr onMouseEnter={() => setHighlightedFieldPath("invoice_number")}>
              <td className="field-label">Invoice #:</td>
              <td>{invoice.invoice_number}</td>
            </tr>
            <tr onMouseEnter={() => setHighlightedFieldPath("invoice_date")}>
              <td className="field-label">Date:</td>
              <td>{invoice.invoice_date}</td>
            </tr>
            <tr onMouseEnter={() => setHighlightedFieldPath("subtotal.total")}>
              <td className="field-label">Total:</td>
              <td className="amount">${invoice.subtotal.total.toFixed(2)}</td>
            </tr>
            <tr>
              <td className="field-label">Currency:</td>
              <td>{invoice.currency || "USD"}</td>
            </tr>
            <tr>
              <td className="field-label">Net Terms:</td>
              <td>{invoice.net_terms || "Net 30"}</td>
            </tr>
          </tbody>
        </table>

        <h4>Line Items ({invoice.items.length})</h4>
        <table className="items-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Description</th>
              <th>Qty</th>
              <th>Unit Price</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {invoice.items.map((item, idx) => (
              <tr key={idx} onMouseEnter={() => setHighlightedFieldPath(`items[${idx}].description`)}>
                <td>{idx + 1}</td>
                <td className="truncate">{item.description.substring(0, 40)}...</td>
                <td>{item.quantity}</td>
                <td>${(item.unit_price || 0).toFixed(2)}</td>
                <td>${item.total_price.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderContractFields = () => {
    if (!contract) return <div className="placeholder">No contract extracted</div>;

    return (
      <div className="extraction-section">
        <h4>Contract Details</h4>
        <table className="fields-table">
          <tbody>
            <tr>
              <td className="field-label">Vendor:</td>
              <td>{contract.vendor_name}</td>
            </tr>
            <tr>
              <td className="field-label">Contract ID:</td>
              <td>{contract.contract_id}</td>
            </tr>
            <tr>
              <td className="field-label">Currency:</td>
              <td>{contract.currency || "USD"}</td>
            </tr>
            <tr>
              <td className="field-label">Net Terms:</td>
              <td>{contract.net_terms || "Net 30"}</td>
            </tr>
            <tr>
              <td className="field-label">Tax Rate:</td>
              <td>{(contract.default_tax_rate * 100).toFixed(2)}%</td>
            </tr>
            <tr>
              <td className="field-label">Allowed Variance:</td>
              <td>{contract.allowed_variance_pct}%</td>
            </tr>
          </tbody>
        </table>

        <h4>Contract Line Items ({contract.line_items.length})</h4>
        <table className="items-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Description</th>
              <th>Unit Price</th>
              <th>Max Qty</th>
            </tr>
          </thead>
          <tbody>
            {contract.line_items.map((item, idx) => (
              <tr key={idx}>
                <td>{idx + 1}</td>
                <td className="truncate">{item.description.substring(0, 40)}...</td>
                <td>${item.unit_price.toFixed(2)}</td>
                <td>{item.max_quantity || "Unlimited"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="extraction-pane">
      <h3>Extracted Fields</h3>
      <div className="extraction-content">
        {renderInvoiceFields()}
        {renderContractFields()}
      </div>
    </div>
  );
};

