import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import {
  buildKpiLiveBannerModuleDocument,
  getSiteModuleConfig,
  KPI_LIVE_BANNER_MODULE_KEY,
  parseKpiLiveBannerPayload,
  patchSiteModuleConfig,
  resolveModuleConfigEtag,
} from '../../api/module-config-client';
import { useAuthPort } from '../../app/auth/AuthRuntimeProvider';
import {
  KPI_LIVE_BANNER_DEFAULTS,
  kpiLiveBannerPayloadToSettings,
  kpiLiveBannerSettingsToPayload,
  mergeKpiLiveBannerSettings,
  type KpiLiveBannerSettings,
} from './kpi-live-banner-settings';

export type KpiLiveBannerSettingsUpdateOptions = {
  /** Motif saisi en UI admin (traçabilité locale jusqu’à journalisation serveur P2). */
  readonly motif?: string;
};

export type KpiLiveBannerSettingsContextValue = {
  readonly settings: KpiLiveBannerSettings;
  readonly updateSettings: (
    partial: Partial<KpiLiveBannerSettings>,
    options?: KpiLiveBannerSettingsUpdateOptions,
  ) => Promise<boolean>;
  readonly reloadConfig: () => Promise<void>;
  readonly isLoading: boolean;
  readonly saveError: string | null;
  /** `true` lorsque les réglages proviennent du GET module-config (site connu). */
  readonly isServerSource: boolean;
  /** `true` quand un PATCH peut être tenté sans risquer d'écraser la vérité serveur. */
  readonly canSave: boolean;
  readonly lastSavedAt: number | null;
  readonly lastSaveMotif: string | null;
};

const KpiLiveBannerSettingsReactContext = createContext<KpiLiveBannerSettingsContextValue | null>(null);

function moduleConfigLoadErrorMessage(status: number, detail: string): string {
  if (status === 403) {
    return 'Vous n’avez pas les droits pour lire la configuration des modules sur ce site. Vérifiez votre profil ou le site actif.';
  }
  if (status === 404) {
    return 'Site introuvable ou configuration modules indisponible pour ce site.';
  }
  if (status === 0) {
    return 'Impossible de joindre le serveur. Vérifiez la connexion réseau puis utilisez « Recharger la configuration ».';
  }
  const base = detail.trim() || 'Le chargement de la configuration a échoué.';
  return `${base} Utilisez le bouton « Recharger la configuration » ci-dessous.`;
}

/**
 * Source unique pour la visibilité / intervalle du bandeau KPI — charge l’API module-config par site
 * quand `siteId` est présent dans l’enveloppe ; défauts locaux sinon.
 */
export function KpiLiveBannerSettingsProvider({ children }: { readonly children: ReactNode }): ReactNode {
  const auth = useAuthPort();
  const siteId = auth.getContextEnvelope().siteId;
  const [settings, setSettings] = useState<KpiLiveBannerSettings>(KPI_LIVE_BANNER_DEFAULTS);
  const [isLoading, setIsLoading] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [isServerSource, setIsServerSource] = useState(false);
  const [canSave, setCanSave] = useState(false);
  const [lastSavedAt, setLastSavedAt] = useState<number | null>(null);
  const [lastSaveMotif, setLastSaveMotif] = useState<string | null>(null);
  const etagRef = useRef<string | null>(null);
  const loadGenerationRef = useRef(0);

  const loadFromServer = useCallback(async () => {
    if (!siteId) {
      setSettings({ ...KPI_LIVE_BANNER_DEFAULTS });
      setIsServerSource(false);
      setCanSave(false);
      etagRef.current = null;
      setSaveError(null);
      setIsLoading(false);
      return;
    }

    const generation = ++loadGenerationRef.current;
    setIsLoading(true);
    setSaveError(null);

    const ac = new AbortController();
    const res = await getSiteModuleConfig(auth, siteId, KPI_LIVE_BANNER_MODULE_KEY, ac.signal);
    if (generation !== loadGenerationRef.current) return;

    if (res.ok) {
      etagRef.current = resolveModuleConfigEtag(res.etag, res.data.version);
      const payload = parseKpiLiveBannerPayload(res.data.payload);
      if (payload) {
        setSettings(kpiLiveBannerPayloadToSettings(payload));
        setIsServerSource(true);
        setCanSave(true);
      } else {
        setSettings({ ...KPI_LIVE_BANNER_DEFAULTS });
        setIsServerSource(false);
        setCanSave(false);
        etagRef.current = null;
        setSaveError(
          'La configuration du bandeau d’indicateurs sur le serveur est illisible. Utilisez « Recharger la configuration » ou contactez le support si le problème persiste.',
        );
      }
    } else {
      etagRef.current = null;
      setSettings({ ...KPI_LIVE_BANNER_DEFAULTS });
      setIsServerSource(false);
      setCanSave(false);
      setSaveError(moduleConfigLoadErrorMessage(res.status, res.detail));
    }
    setIsLoading(false);
  }, [auth, siteId]);

  useEffect(() => {
    void loadFromServer();
  }, [loadFromServer]);

  const reloadConfig = useCallback(async () => {
    await loadFromServer();
  }, [loadFromServer]);

  const updateSettings = useCallback(
    async (
      partial: Partial<KpiLiveBannerSettings>,
      options?: KpiLiveBannerSettingsUpdateOptions,
    ): Promise<boolean> => {
      const next = mergeKpiLiveBannerSettings(settings, partial);
      if (!siteId) {
        setSettings(next);
        setSaveError('Aucun site actif : sélectionnez un site avant d’enregistrer.');
        return false;
      }
      if (!etagRef.current || !canSave) {
        setSaveError(
          'Impossible d’enregistrer : la configuration n’a pas pu être chargée depuis le serveur. Cliquez sur « Recharger la configuration ».',
        );
        return false;
      }

      setSaveError(null);
      const payload = kpiLiveBannerSettingsToPayload(next);
      const body = buildKpiLiveBannerModuleDocument(payload);
      const res = await patchSiteModuleConfig(auth, siteId, KPI_LIVE_BANNER_MODULE_KEY, body, {
        ifMatch: etagRef.current,
        changeReason: options?.motif,
      });
      if (!res.ok) {
        const detail = res.detail.trim() || 'L’enregistrement a échoué.';
        setSaveError(
          res.status === 403
            ? `${detail} Vérifiez vos droits sur ce site.`
            : res.status === 412
              ? `${detail} Rechargez la configuration puis réessayez.`
              : detail,
        );
        return false;
      }
      etagRef.current = resolveModuleConfigEtag(res.etag, res.data.version);
      const parsed = parseKpiLiveBannerPayload(res.data.payload);
      if (parsed) {
        setSettings(kpiLiveBannerPayloadToSettings(parsed));
      } else {
        setSettings(next);
      }
      setIsServerSource(true);
      setCanSave(true);
      setLastSavedAt(Date.now());
      setLastSaveMotif(options?.motif?.trim() ? options.motif.trim() : null);
      return true;
    },
    [auth, canSave, settings, siteId],
  );

  const value = useMemo<KpiLiveBannerSettingsContextValue>(
    () => ({
      settings,
      updateSettings,
      reloadConfig,
      isLoading,
      saveError,
      isServerSource,
      canSave,
      lastSavedAt,
      lastSaveMotif,
    }),
    [settings, updateSettings, reloadConfig, isLoading, saveError, isServerSource, canSave, lastSavedAt, lastSaveMotif],
  );

  return (
    <KpiLiveBannerSettingsReactContext.Provider value={value}>{children}</KpiLiveBannerSettingsReactContext.Provider>
  );
}

export function useKpiLiveBannerSettings(): KpiLiveBannerSettingsContextValue {
  const ctx = useContext(KpiLiveBannerSettingsReactContext);
  if (!ctx) {
    throw new Error(
      'useKpiLiveBannerSettings : enveloppez l’application avec <KpiLiveBannerSettingsProvider> (voir RootProviders).',
    );
  }
  return ctx;
}
