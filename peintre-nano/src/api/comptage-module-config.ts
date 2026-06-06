import { useEffect, useState } from 'react';
import type { AuthContextPort } from '../app/auth/auth-context-port';
import { getSiteModuleConfig, type ModuleConfigDocumentDto } from './module-config-client';

export const COMPTAGE_PIECES_BILLETS_MODULE_KEY = 'comptage-pieces-billets' as const;

export type ComptageModulePayload = {
  readonly enabled: boolean;
  readonly show_images: boolean;
  readonly skip_allowed: boolean;
  readonly require_denomination_grid: boolean;
};

export const DEFAULT_COMPTAGE_MODULE_PAYLOAD: ComptageModulePayload = {
  enabled: false,
  show_images: true,
  skip_allowed: true,
  require_denomination_grid: false,
};

export function parseComptageModulePayload(payload: Record<string, unknown>): ComptageModulePayload {
  return {
    enabled: payload.enabled === true,
    show_images: payload.show_images !== false,
    skip_allowed: payload.skip_allowed !== false,
    require_denomination_grid: payload.require_denomination_grid === true,
  };
}

export function parseComptageModuleDocument(doc: ModuleConfigDocumentDto): ComptageModulePayload {
  return parseComptageModulePayload(doc.payload);
}

export type ComptageModuleConfigState = {
  readonly loading: boolean;
  readonly config: ComptageModulePayload;
  readonly moduleEnabled: boolean;
};

/**
 * Charge `GET module-config/comptage-pieces-billets` — signal autoritaire pour le wizard clôture (Story 9.12).
 * 404 / erreur réseau → module désactivé (parité legacy).
 */
export function useComptageModuleConfig(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  siteId: string | null | undefined,
): ComptageModuleConfigState {
  const [loading, setLoading] = useState(Boolean(siteId?.trim()));
  const [config, setConfig] = useState<ComptageModulePayload>(DEFAULT_COMPTAGE_MODULE_PAYLOAD);

  useEffect(() => {
    const sid = siteId?.trim();
    if (!sid) {
      setConfig(DEFAULT_COMPTAGE_MODULE_PAYLOAD);
      setLoading(false);
      return;
    }

    let cancelled = false;
    const ac = new AbortController();
    setLoading(true);

    void (async () => {
      const res = await getSiteModuleConfig(auth, sid, COMPTAGE_PIECES_BILLETS_MODULE_KEY, ac.signal);
      if (cancelled) return;
      if (!res.ok) {
        setConfig(DEFAULT_COMPTAGE_MODULE_PAYLOAD);
        setLoading(false);
        return;
      }
      setConfig(parseComptageModuleDocument(res.data));
      setLoading(false);
    })();

    return () => {
      cancelled = true;
      ac.abort();
    };
  }, [auth, siteId]);

  return {
    loading,
    config,
    moduleEnabled: config.enabled,
  };
}
