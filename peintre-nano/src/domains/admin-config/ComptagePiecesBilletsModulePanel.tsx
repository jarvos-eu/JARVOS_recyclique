import { Alert, Button, Group, Stack, Text } from '@mantine/core';
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  COMPTAGE_PIECES_BILLETS_MODULE_KEY,
  parseComptageModuleDocument,
} from '../../api/comptage-module-config';
import { getSiteModuleConfig, patchSiteModuleConfig } from '../../api/module-config-client';
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

  useEffect(() => {
    if (!siteId) {
      setSettings({ ...COMPTAGE_PIECES_BILLETS_DEFAULTS });
      setDraft({ ...COMPTAGE_PIECES_BILLETS_DEFAULTS });
      setCanSave(false);
      etagRef.current = null;
      return;
    }

    let cancelled = false;
    const ac = new AbortController();
    setIsLoading(true);
    setSaveError(null);

    void (async () => {
      const res = await getSiteModuleConfig(auth, siteId, COMPTAGE_PIECES_BILLETS_MODULE_KEY, ac.signal);
      if (cancelled) return;
      if (res.ok) {
        etagRef.current = res.etag;
        const parsed = comptagePayloadToSettings(parseComptageModuleDocument(res.data));
        setSettings(parsed);
        setDraft(parsed);
        setCanSave(Boolean(res.etag));
        setDirty(false);
      } else {
        etagRef.current = null;
        setSettings({ ...COMPTAGE_PIECES_BILLETS_DEFAULTS });
        setDraft({ ...COMPTAGE_PIECES_BILLETS_DEFAULTS });
        setCanSave(false);
        setSaveError(`${res.detail} Rechargez avant toute tentative d'enregistrement.`);
      }
      setIsLoading(false);
    })();

    return () => {
      cancelled = true;
      ac.abort();
    };
  }, [auth, siteId]);

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
      setSaveError("Configuration serveur non chargée. Rechargez avant toute tentative d'enregistrement.");
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
      setSaveError(res.detail);
      return;
    }
    etagRef.current = res.etag;
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
          Enregistrement désactivé tant que la configuration serveur n'a pas été rechargée avec succès.
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
