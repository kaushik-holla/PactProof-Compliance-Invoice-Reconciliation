
import axios, { AxiosInstance } from "axios";
import {
  Invoice,
  Contract,
  ReconcileResponse,
  ExtractionResponse,
  NoteGenerationRequest,
  NoteGenerationResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  async health() {
    return this.client.get("/health");
  }

  async uploadFile(file: File): Promise<{ filename: string; file_url: string }> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await this.client.post("/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  }

  async parseExtractInvoice(file: File): Promise<ExtractionResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await this.client.post("/parse_extract/invoice", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  }

  async parseExtractContract(file: File): Promise<ExtractionResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await this.client.post("/parse_extract/contract", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  }

  async reconcile(invoice: Invoice, contract: Contract): Promise<ReconcileResponse> {
    const response = await this.client.post("/reconcile", {
      invoice,
      contract,
    });
    return response.data;
  }

  async draftNote(request: NoteGenerationRequest): Promise<NoteGenerationResponse> {
    const response = await this.client.post("/draft_note", request);
    return response.data;
  }

  async exportNotePdf(noteText: string, invoiceNumber?: string): Promise<Blob> {
    const response = await this.client.post(
      "/export_note_pdf",
      {
        note_text: noteText,
        invoice_number: invoiceNumber,
      },
      {
        responseType: "blob",
      }
    );
    return response.data;
  }
}

export const apiClient = new ApiClient();

