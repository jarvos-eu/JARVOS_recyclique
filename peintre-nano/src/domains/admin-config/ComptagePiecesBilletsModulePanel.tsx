import { Alert, Button, Group, Stack, Text } from '@mantine/core';
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  COMPTAGE_PIECES_BILLETS_MODULE_KEY,
  parseComptageModuleDocument,
} from '../../api/comptage-module-config';
import { getSiteModuleConfig, patchSiteModuleConfig, resolveModuleConfigEtag } from '../../api/module-config-client';
import { useAuthPort } from '../../app/auth/AuthRuntimeProvider';
import {
  COMPTAGE_PIECES_BILLETS_DEFAULTS,
  COMPTAGE_PIECES_BILLETS_SCHEMA_VERSION,
  comptagePayloadToSettings,
  comptageSettingsToPayload,
  mergeComptagePiecesBilletsSettings,
  type ComptagePiecesBilletsSettings,
} from './comptage-pieces-billets-settings';
import { ComptagePiecesBilletsSettingsFields } from './ComptagePiecesBilletsSettingsFields';

export type ComptagePiecesBilletsModulePanelProps = {
  readonly motif: string;
  readonly disabled?: boolean;
};

function comptageLoadErrorMessage(status: number, detail: string): string {
  if (status === 403) {
    return 'Vous n’avez pas les droits pour lire la configuration comptage sur ce site.';
  }
  if (status === 404) {
    return 'Configuration comptage introuvable pour ce site.';
  }
  if (status === 0) {
    return 'Impossible de joindre le serveur pour charger le module comptage.';
  }
  const base = detail.trim() || 'Le chargement a échoué.';
  return `${base} Rechargez la page ou réessayez dans quelques instants.`;
}

/** Panneau admin autonome pour le module comptage — GET/PATCH module-config serveur. */
export function ComptagePiecesBilletsModulePanel({ motif, disabled = false }: ComptagePiecesBilletsModulePanelProps) {
  const auth = useAuthPort();
  const siteId = auth.getContextEnvelope().siteId;
  const [settings, setSettings] = useState<ComptagePiecesBilletsSettings>(COMPTAGE_PIECES_BILLETS_DEFAULTS);
  const [draft, setDraft] = useState<ComptagePiecesBilletsSettings>(COMPTAGE_PIECES_BILLETS_DEFAULTS);
  const [dirty, setDirty] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [canSave, setCanSave] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const etagRef = useRef<string | null>(null);

  const loadFromServer = useCallback(async () => {
    if (!siteId) {
      setSettings({ ...COMPTAGE_PIECES_BILLETS_DEFAULTS });
      setDraft({ ...COMPTAGE_PIECES_BILLETS_DEFAULTS });
      setCanSave(false);
      etagRef.current = null;
      return;
    }

    setIsLoading(true);
    setSaveError(null);
    const ac = new AbortController();
    const res = await getSiteModuleConfig(auth, siteId, COMPTAGE_PIECES_BILLETS_MODULE_KEY, ac.signal);
    if (res.ok) {
      etagRef.current = resolveModuleConfigEtag(res.etag, res.data.version);
      const parsed = comptagePayloadToSettings(parseComptageModuleDocument(res.data));
      setSettings(parsed);
      setDraft(parsed);
      setCanSave(true);
      setDirty(false);
    } else {
      etagRef.current = null;
      setSettings({ ...COMPTAGE_PIECES_BILLETS_DEFAULTS });
      setDraft({ ...COMPTAGE_PIECES_BILLETS_DEFAULTS });
      setCanSave(false);
      setSaveError(comptageLoadErrorMessage(res.status, res.detail));
    }
    setIsLoading(false);
  }, [auth, siteId]);

  useEffect(() => {
    void loadFromServer();
  }, [loadFromServer]);

  useEffect(() => {
    setDraft(settings);
    setDirty(false);
  }, [settings]);

  const onDraftChange = useCallback((partial: Partial<ComptagePiecesBilletsSettings>) => {
    setDraft((prev) => mergeComptagePiecesBilletsSettings(prev, partial));
    setDirty(true);
    setSaveSuccess(null);
  }, []);

  const handleSave = useCallback(async () => {
    if (!siteId || !etagRef.current || !canSave) {
      setSaveError(
        'Impossible d’enregistrer : la configuration comptage n’a pas pu être chargée. Rechargez la page puis réessayez.',
      );
      return;
    }
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(null);
    const body = {
      schema_version: COMPTAGE_PIECES_BILLETS_SCHEMA_VERSION,
      payload: comptageSettingsToPayload(draft),
    };
    const res = await patchSiteModuleConfig(auth, siteId, COMPTAGE_PIECES_BILLETS_MODULE_KEY, body, {
      ifMatch: etagRef.current,
      changeReason: motif.trim() || undefined,
    });
    setSaving(false);
    if (!res.ok) {
      const detail = res.detail.trim() || 'L’enregistrement comptage a échoué.';
      setSaveError(
        res.status === 412
          ? `${detail} Rechargez la configuration du module puis réessayez.`
          : detail,
      );
      return;
    }
    etagRef.current = resolveModuleConfigEtag(res.etag, res.data.version);
    const parsed = comptagePayloadToSettings(parseComptageModuleDocument(res.data));
    setSettings(parsed);
    setDraft(parsed);
    setDirty(false);
    setCanSave(true);
    setSaveSuccess('Configuration comptage enregistrée sur le serveur pour ce site.');
  }, [auth, canSave, draft, motif, siteId]);

  return (
    <Stack gap="md" data-testid="comptage-pieces-billets-module-panel">
      <Text size="sm" c="dimmed">
        Effet : lorsque le module est activé, le wizard de clôture caisse inclut l'étape comptage pièces/billets
        avant la validation finale. Désactivé → parité legacy (montant compté seul).
      </Text>
      {!canSave && !isLoading ? (
        <Text size="sm" c="orange">
          Enregistrement indisponible : la configuration n’a pas pu être lue depuis le serveur.
        </Text>
      ) : null}
      <ComptagePiecesBilletsSettingsFields
        value={draft}
        onChange={onDraftChange}
        disabled={disabled || isLoading || saving}
      />
      {saveError ? (
        <Alert color="red" title="Erreur comptage" data-testid="admin-comptage-save-error">
          {saveError}
        </Alert>
      ) : null}
      {saveSuccess ? (
        <Alert color="green" title="Enregistré" data-testid="admin-comptage-save-success">
          {saveSuccess}
        </Alert>
      ) : null}
      <Group justify="flex-end">
        <Button
          onClick={() => void handleSave()}
          loading={saving}
          disabled={!dirty || isLoading || !canSave || disabled}
          data-testid="admin-comptage-save"
        >
          Enregistrer le module comptage
        </Button>
      </Group>
    </Stack>
  );
}
