import {
  Accordion,
  Alert,
  Badge,
  Button,
  Group,
  Paper,
  Stack,
  Text,
  Textarea,
  Title,
  Tooltip,
} from '@mantine/core';
import { Info, LayoutGrid, RefreshCw } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import { KPI_LIVE_BANNER_MODULE_KEY } from '../../api/module-config-client';
import { COMPTAGE_PIECES_BILLETS_MODULE_KEY } from '../../api/comptage-module-config';
import { useAuthPort } from '../../app/auth/AuthRuntimeProvider';
import {
  mergeKpiLiveBannerSettings,
  type KpiLiveBannerSettings,
} from '../bandeau-live/kpi-live-banner-settings';
import { useKpiLiveBannerSettings } from '../bandeau-live/kpi-live-banner-settings-provider';
import type { RegisteredWidgetProps } from '../../registry/widget-registry';
import { ADMIN_TRANSVERSE_LIST_PAGE_MANIFEST_GUARDS } from './admin-transverse-list-page-guards';
import { KpiLiveBannerSettingsFields } from './KpiLiveBannerSettingsFields';
import { ComptagePiecesBilletsModulePanel } from './ComptagePiecesBilletsModulePanel';
import { useAdminSiteDisplayLabel } from './use-admin-site-display-label';

const MODULES_CATALOG = [
  {
    moduleKey: KPI_LIVE_BANNER_MODULE_KEY,
    title: 'Bandeau indicateurs live (KPI)',
    description:
      'Affiche les indicateurs en direct sur la caisse et la réception, avec une fréquence de rafraîchissement réglable.',
  },
  {
    moduleKey: COMPTAGE_PIECES_BILLETS_MODULE_KEY,
    title: 'Comptage pièces / billets (clôture)',
    description:
      "Active l'étape comptage détaillé dans le wizard de clôture caisse — grille 15 lignes, relecture, pictos optionnels.",
  },
] as const;

/**
 * Panneau « Gestion des modules » — shell Story 9.6 ; pilote `kpi-live-banner` via module-config serveur.
 */
export function AdminModulesWidget(_props: RegisteredWidgetProps) {
  const auth = useAuthPort();
  const envelope = auth.getContextEnvelope();
  const siteId = envelope.siteId;
  const siteDisplay = useAdminSiteDisplayLabel(siteId);
  const isAdminModulesAllowed = ADMIN_TRANSVERSE_LIST_PAGE_MANIFEST_GUARDS.requiredPermissionKeys.every((key) =>
    envelope.permissions.permissionKeys.includes(key),
  );

  const {
    settings,
    updateSettings,
    reloadConfig,
    isLoading,
    saveError,
    isServerSource,
    canSave,
    lastSavedAt,
    lastSaveMotif,
  } = useKpiLiveBannerSettings();
  const [draft, setDraft] = useState<KpiLiveBannerSettings>(settings);
  const [dirty, setDirty] = useState(false);
  const [motif, setMotif] = useState('');
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [reloading, setReloading] = useState(false);

  useEffect(() => {
    setDraft(settings);
    setDirty(false);
  }, [settings]);

  const onDraftChange = useCallback(
    (partial: Partial<KpiLiveBannerSettings>) => {
      setDraft((prev) => mergeKpiLiveBannerSettings(prev, partial));
      setDirty(true);
      setSaveSuccess(null);
    },
    [],
  );

  const handleSave = useCallback(async () => {
    setSaving(true);
    setSaveSuccess(null);
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
      setSaveSuccess('Configuration enregistrée sur le serveur pour ce site.');
    }
  }, [draft, motif, updateSettings]);

  const handleReload = useCallback(async () => {
    setReloading(true);
    setSaveSuccess(null);
    await reloadConfig();
    setReloading(false);
  }, [reloadConfig]);

  if (!isAdminModulesAllowed) {
    return (
      <Alert color="gray" title="Accès réservé" data-testid="admin-modules-denied">
        Cet écran est réservé aux profils d’administration du site actif.
      </Alert>
    );
  }

  if (!siteId) {
    return (
      <Alert color="yellow" title="Site requis" data-testid="admin-modules-no-site">
        Sélectionnez un site actif pour gérer les modules.
      </Alert>
    );
  }

  const rolesLine = envelope.permissions.permissionKeys.includes('caisse.sale_correct')
    ? 'Super-admin : peut agir sur tous les sites (ici le site actif de la session).'
    : 'Administrateur responsable : peut agir sur son site affecté uniquement.';

  return (
    <Stack gap="md" data-testid="admin-modules-widget">
      <div>
        <Title
          order={1}
          size="h2"
          style={{ display: 'flex', alignItems: 'center', gap: 8 }}
          data-testid="admin-modules-title"
        >
          <LayoutGrid size={22} aria-hidden />
          Gestion des modules
        </Title>
        <Text size="sm" c="dimmed" mt={4}>
          Activez et réglez les modules pour le site courant.
        </Text>
      </div>

      <Paper p="md" withBorder radius="md" data-testid="admin-modules-roles-scope">
        <Stack gap="xs">
          <Text size="sm" fw={600}>
            Qui peut agir
          </Text>
          <Text size="sm">{rolesLine}</Text>
          <Text size="sm" fw={600} mt="xs">
            Périmètre
          </Text>
          <Group gap="xs">
            <Text size="sm">Site :</Text>
            <Badge
              variant="light"
              data-testid="admin-modules-site-label"
              title={siteDisplay.fullId ? `Identifiant technique : ${siteDisplay.fullId}` : undefined}
            >
              {siteDisplay.label}
            </Badge>
          </Group>
          <Group gap={6} align="flex-start">
            <Text size="sm" c="dimmed" style={{ flex: 1 }}>
              Les réglages s’appliquent à tous les postes de ce site après enregistrement.
            </Text>
            <Tooltip
              label="Détail technique : synchronisation périodique des indicateurs live et enregistrement centralisé sur le serveur Recyclique."
              multiline
              w={280}
            >
              <span style={{ display: 'inline-flex', cursor: 'help' }} aria-label="Informations techniques">
                <Info size={16} aria-hidden />
              </span>
            </Tooltip>
          </Group>
          {isServerSource ? (
            <Badge color="green" variant="light" size="sm" data-testid="admin-modules-server-source">
              Synchronisé avec le serveur
            </Badge>
          ) : (
            <Badge color="gray" variant="light" size="sm">
              Valeurs par défaut locales
            </Badge>
          )}
          {!canSave && !isLoading ? (
            <Text size="sm" c="orange">
              Enregistrement indisponible tant que la configuration serveur n’a pas été chargée correctement.
            </Text>
          ) : null}
          <Button
            size="xs"
            variant="light"
            leftSection={<RefreshCw size={14} />}
            loading={reloading || isLoading}
            onClick={() => void handleReload()}
            data-testid="admin-modules-reload-config"
          >
            Recharger la configuration
          </Button>
        </Stack>
      </Paper>

      <details data-testid="admin-modules-motif-details">
        <summary style={{ cursor: 'pointer', fontSize: 14 }}>
          Note interne (optionnel)
        </summary>
        <Textarea
          aria-label="Note interne (optionnel)"
          placeholder="Ex. masquage bandeau pendant inventaire"
          value={motif}
          onChange={(e) => setMotif(e.currentTarget.value)}
          minRows={2}
          mt="xs"
          data-testid="admin-modules-patch-motif"
        />
      </details>

      {saveError ? (
        <Alert color="red" title="Erreur" data-testid="admin-modules-save-error">
          {saveError}
        </Alert>
      ) : null}
      {saveSuccess ? (
        <Alert color="green" title="Enregistré" data-testid="admin-modules-save-success">
          {saveSuccess}
          {lastSaveMotif ? (
            <Text size="sm" mt={4}>
              Note indiquée : {lastSaveMotif}
            </Text>
          ) : null}
          {lastSavedAt ? (
            <Text size="xs" c="dimmed" mt={4}>
              Horodatage local : {new Date(lastSavedAt).toLocaleString('fr-FR')}
            </Text>
          ) : null}
        </Alert>
      ) : null}

      <Accordion variant="separated" defaultValue={KPI_LIVE_BANNER_MODULE_KEY}>
        {MODULES_CATALOG.map((mod) => (
          <Accordion.Item key={mod.moduleKey} value={mod.moduleKey}>
            <Accordion.Control data-testid={`admin-modules-accordion-${mod.moduleKey}`}>
              {mod.title}
            </Accordion.Control>
            <Accordion.Panel>
              <Stack gap="md">
                <Text size="sm" c="dimmed">
                  {mod.description}
                </Text>
                <details>
                  <summary style={{ cursor: 'pointer', fontSize: 12 }}>
                    <Text span size="xs" c="dimmed" component="span">
                      Pour les techniciens
                    </Text>
                  </summary>
                  <Text size="xs" c="dimmed" mt={6}>
                    Identifiant module : {mod.moduleKey}
                  </Text>
                </details>
                {mod.moduleKey === KPI_LIVE_BANNER_MODULE_KEY ? (
                  <KpiLiveBannerSettingsFields
                    value={draft}
                    onChange={onDraftChange}
                    disabled={isLoading || saving}
                  />
                ) : mod.moduleKey === COMPTAGE_PIECES_BILLETS_MODULE_KEY ? (
                  <ComptagePiecesBilletsModulePanel motif={motif} disabled={saving} />
                ) : null}
              </Stack>
            </Accordion.Panel>
          </Accordion.Item>
        ))}
      </Accordion>

      <Group justify="flex-end">
        <Button
          onClick={() => void handleSave()}
          loading={saving}
          disabled={!dirty || isLoading || !canSave}
          data-testid="admin-modules-save"
        >
          Enregistrer les modifications
        </Button>
      </Group>
    </Stack>
  );
}
