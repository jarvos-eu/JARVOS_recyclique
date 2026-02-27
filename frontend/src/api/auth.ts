/**
 * Client API auth — Story 3.1, 3.3.
 * POST /v1/auth/login, POST /v1/auth/pin (déverrouillage caisse).
 */

const getBase = (): string =>
  (import.meta.env?.VITE_API_BASE_URL as string) ?? '';

export interface UserInToken {
  id: string;
  username: string;
  email: string;
  role: string;
  status: string;
  first_name: string | null;
  last_name: string | null;
}

export interface PinLoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserInToken;
  permissions?: string[];
}

/**
 * Déverrouillage caisse par PIN — POST /v1/auth/pin.
 * En cas de succès : tokens + user. 401 si PIN invalide, 403 si pas permission caisse.
 */
export async function postPinUnlock(pin: string): Promise<PinLoginResponse> {
  const base = getBase();
  const res = await fetch(`${base}/v1/auth/pin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pin }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const message = typeof data?.detail === 'string' ? data.detail : 'Erreur de déverrouillage';
    throw new Error(message);
  }
  return res.json() as Promise<PinLoginResponse>;
}
