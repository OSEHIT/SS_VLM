// =============================================================================
// Smart Shelf V2 — API Service
// =============================================================================
// Wrappers pour les appels réseau vers le backend FastAPI.
// =============================================================================

import { API_BASE_URL } from "../config/api";

// ---------------------------------------------------------------------------
// Error Helpers
// ---------------------------------------------------------------------------

/**
 * Converts raw fetch errors into user-friendly messages.
 */
export function friendlyError(err: unknown): string {
  if (err instanceof TypeError) {
    // Network-level failure (no response at all)
    return "Impossible de joindre le serveur. Vérifiez votre connexion ou l'adresse du serveur.";
  }
  if (err instanceof Error) {
    return err.message;
  }
  return "Une erreur inconnue est survenue.";
}

/**
 * Builds a user-friendly message from an HTTP response.
 */
function httpError(status: number, detail?: string): string {
  if (status === 404) {
    return "Route introuvable sur le serveur (404). Vérifiez la version de l'API.";
  }
  if (status >= 500) {
    return `Erreur serveur (${status}). Réessayez plus tard.`;
  }
  return detail || `Erreur HTTP ${status}`;
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export interface ScanResult {
  scan_id: string | null;
  product_name: string | null;
  brand: string | null;
  expiry_date: string | null;
  quantity: number | null;
  ean: string | null;
  source: string;
  confidence: number;
  product_type: "packaged" | "bulk";
  image_url: string | null;
  display_image: string | null;
  raw_vlm_output: string | null;
}

export interface Product {
  id: string;
  product_name: string | null;
  brand: string | null;
  expiry_date: string | null;
  ean: string | null;
  product_type: "packaged" | "bulk";
  quantity: number | null;
  source: string | null;
  confidence: number;
  image_url: string | null;
  image_base64: string | null;
  display_image: string | null;
  scan_id: string | null;
  notification_ids: string[] | null;
  created_at?: string;
}

export interface ProductCreate {
  product_name: string | null;
  brand: string | null;
  expiry_date: string | null;
  ean: string | null;
  product_type: "packaged" | "bulk";
  quantity: number | null;
  source: string | null;
  confidence: number;
  image_url: string | null;
  image_base64: string | null;
  display_image: string | null;
  scan_id: string | null;
  notification_ids: string[] | null;
}

// ---------------------------------------------------------------------------
// Scan
// ---------------------------------------------------------------------------
export async function scanProduct(
  imageUris: string[],
  isBulk: boolean
): Promise<ScanResult> {
  const formData = new FormData();

  imageUris.forEach((uri, index) => {
    formData.append("images", {
      uri,
      name: `photo_${index}.jpg`,
      type: "image/jpeg",
    } as any);
  });

  const url = `${API_BASE_URL}/scan?is_bulk=${isBulk}`;

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
      },
      body: formData,
    });
  } catch (err) {
    throw new Error(friendlyError(err));
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(httpError(response.status, errorData.detail));
  }

  return response.json();
}

// ---------------------------------------------------------------------------
// Products CRUD
// ---------------------------------------------------------------------------
export async function fetchProducts(
  skip = 0,
  limit = 100
): Promise<Product[]> {
  let response: Response;
  try {
    response = await fetch(
      `${API_BASE_URL}/products/?skip=${skip}&limit=${limit}`
    );
  } catch (err) {
    throw new Error(friendlyError(err));
  }

  if (!response.ok) {
    throw new Error(httpError(response.status));
  }

  return response.json();
}

export async function fetchProduct(id: string): Promise<Product> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/products/${id}`);
  } catch (err) {
    throw new Error(friendlyError(err));
  }

  if (!response.ok) {
    throw new Error(httpError(response.status));
  }

  return response.json();
}

export async function createProduct(data: ProductCreate): Promise<Product> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/products/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
  } catch (err) {
    throw new Error(friendlyError(err));
  }

  if (!response.ok) {
    throw new Error(httpError(response.status));
  }

  return response.json();
}

export async function updateProduct(
  id: string,
  data: Partial<ProductCreate>
): Promise<Product> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/products/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
  } catch (err) {
    throw new Error(friendlyError(err));
  }

  if (!response.ok) {
    throw new Error(httpError(response.status));
  }

  return response.json();
}

export async function deleteProduct(id: string): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/products/${id}`, {
      method: "DELETE",
    });
  } catch (err) {
    throw new Error(friendlyError(err));
  }

  if (!response.ok) {
    throw new Error(httpError(response.status));
  }
}

// ---------------------------------------------------------------------------
// RL Feedback
// ---------------------------------------------------------------------------
export async function submitRLFeedback(
  scanId: string,
  groundTruth: Record<string, unknown>
): Promise<{ status: string; message: string }> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/rl-feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scan_id: scanId, ground_truth: groundTruth }),
    });
  } catch (err) {
    throw new Error(friendlyError(err));
  }

  if (!response.ok) {
    throw new Error(httpError(response.status));
  }

  return response.json();
}
