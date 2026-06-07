import { useEffect, useMemo, useState } from 'react';
import { listSitesForAdmin } from '../../api/admin-sites-client';
import { useAuthPort } from '../../app/auth/AuthRuntimeProvider';
import { CONTEXT_ACTIVE_SITE_DISPLAY_NAME_KEY } from '../../runtime/context-presentation-keys';

let siteNameCache: Map<string, string> | null = null;

export type AdminSiteDisplayLabel = {
  readonly label: string;
  /** UUID complet — infobulle expert uniquement. */
  readonly fullId?: string;
};

/**
 * Libellé site lisible pour surfaces admin (REV-TRANSVERSE-04) :
 * presentation_labels → listSitesForAdmin → troncation UUID.
 */
export function useAdminSiteDisplayLabel(siteId: string | null | undefined): AdminSiteDisplayLabel {
  const auth = useAuthPort();
  const envelope = auth.getContextEnvelope();
  const presentationLabel = envelope.presentationLabels?.[CONTEXT_ACTIVE_SITE_DISPLAY_NAME_KEY]?.trim();

  const [siteNames, setSiteNames] = useState<Map<string, string>>(() => siteNameCache ?? new Map());

  useEffect(() => {
    if (!siteId || presentationLabel) return;
    let cancelled = false;
    void (async () => {
      const res = await listSitesForAdmin(auth, { limit: 200 });
      if (cancelled || !res.ok) return;
      const m = new Map<string, string>();
      for (const s of res.data) m.set(s.id, s.name);
      siteNameCache = m;
      setSiteNames(m);
    })();
    return () => {
      cancelled = true;
    };
  }, [auth, siteId, presentationLabel]);

  return useMemo(() => {
    if (!siteId) return { label: '—' };
    if (presentationLabel) return { label: presentationLabel, fullId: siteId };
    const fromList = siteNames.get(siteId)?.trim();
    if (fromList) return { label: fromList, fullId: siteId };
    return { label: `${siteId.slice(0, 8)}…`, fullId: siteId };
  }, [siteId, presentationLabel, siteNames]);
}
