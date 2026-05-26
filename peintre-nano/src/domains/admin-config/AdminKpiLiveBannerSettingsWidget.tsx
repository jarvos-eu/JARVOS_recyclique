import { Alert, Button, Group, Paper, Stack, Text, Textarea, Title } from '@mantine/core';
import { BarChart3 } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import { useAuthPort } from '../../app/auth/AuthRuntimeProvider';
import type { RegisteredWidgetProps } from '../../registry/widget-registry';
import {
  mergeKpiLiveBannerSettings,
  type KpiLiveBannerSettings,
} from '../bandeau-live/kpi-live-banner-settings';
import { useKpiLiveBannerSettings } from '../bandeau-live/kpi-live-banner-settings-provider';
import { ADMIN_SUPER_PAGE_MANIFEST_GUARDS } from './admin-super-page-guards';
import { KpiLiveBannerSettingsFields } from './KpiLiveBannerSettingsFields';

/**
 * Réglages bandeau KPI — préférez la page « Gestion des modules » (`/admin/modules`).
 * Même API module-config serveur que {@link AdminModulesWidget}.
 */
export function AdminKpiLiveBannerSettingsWidget(_props: RegisteredWidgetProps) {
  const auth = useAuthPort();
  const envelope = auth.getContextEnvelope();
  const siteId = envelope.siteId;
  const isSuperAdminUi = ADMIN_SUPER_PAGE_MANIFEST_GUARDS.requiredPermissionKeys.every((key) =>
    envelope.permissions.permissionKeys.includes(key),
  );
  const { settings, updateSettings, isLoading, saveError, isServerSource } = useKpiLiveBannerSettings();
  const [draft, setDraft] = useState<KpiLiveBannerSettings>(settings);
  const [dirty, setDirty] = useState(false);
  const [motif, setMotif] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setDraft(settings);
    setDirty(false);
  }, [settings]);

  const onDraftChange = useCallback((partial: Partial<KpiLiveBannerSettings>) => {
    setDraft((prev) => mergeKpiLiveBannerSettings(prev, partial));
    setDirty(true);
  }, []);

  const handleSave = useCallback(async () => {
    setSaving(true);
    const ok = await updateSettings(
      {
        showOnCaisse: draft.showOnCaisse,
        showOnReception: draft.showOnReception,
        refreshIntervalMs: draft.refreshIntervalMs,
      },
      { motif: motif.trim() || undefined },
    );
    setSaving(false);
    if (ok) {
      setDirty(false);
    }
  }, [draft, motif, updateSettings]);

  if (!isSuperAdminUi) {
    return (
      <Alert color="gray" title="Accès réservé" data-testid="admin-kpi-live-settings-denied">
        Cet écran est réservé au profil super-admin.
      </Alert>
    );
  }

  if (!siteId) {
    return (
      <Alert color="yellow" title="Site requis" data-testid="admin-kpi-live-settings-no-site">
        Aucun site dans l’enveloppe de contexte — impossible de charger la configuration serveur.
      </Alert>
    );
  }

  return (
    <Stack gap="md" data-testid="admin-kpi-live-banner-settings">
      <div>
        <Title
          order={1}
          size="h2"
          style={{ display: 'flex', alignItems: 'center', gap: 8 }}
          data-testid="admin-kpi-live-settings-title"
        >
          <BarChart3 size={22} aria-hidden />
          Bandeau indicateurs live (KPI)
        </Title>
        <Text size="sm" c="dimmed" mt={4}>
          Réglages du module <code>kpi-live-banner</code> pour le site{' '}
          <strong data-testid="admin-kpi-live-settings-site-id">{siteId}</strong>. Source de vérité : API{' '}
          <code>module-config</code> (pas le stockage local). Accès : super-admin sur le site actif de
          l’enveloppe.
        </Text>
        {isServerSource ? (
          <Text size="xs" c="teal" mt={4} data-testid="admin-kpi-live-settings-server-sync">
            Synchronisé avec le serveur.
          </Text>
        ) : null}
      </div>

      <Textarea
        label="Motif (optionnel)"
        value={motif}
        onChange={(e) => setMotif(e.currentTarget.value)}
        minRows={2}
        data-testid="admin-kpi-live-settings-motif"
      />

      {saveError ? (
        <Alert color="red" data-testid="admin-kpi-live-settings-error">
          {saveError}
        </Alert>
      ) : null}

      <Paper p="md" withBorder radius="md">
        <KpiLiveBannerSettingsFields value={draft} onChange={onDraftChange} disabled={isLoading || saving} />
      </Paper>

      <Group justify="flex-end">
        <Button
          onClick={() => void handleSave()}
          loading={saving}
          disabled={!dirty || isLoading}
          data-testid="admin-kpi-live-settings-save"
        >
          Enregistrer
        </Button>
      </Group>
    </Stack>
  );
}
