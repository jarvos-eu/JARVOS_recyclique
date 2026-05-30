import {
  Badge,
  Button,
  Group,
  Modal,
  MultiSelect,
  NumberInput,
  Paper,
  Select,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import { RefreshCw } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import {
  createRegisteredDeviceForAdmin,
  issueDeviceEnrollmentCodeForAdmin,
  listRegisteredDevicesForAdmin,
  markDeviceIdentityLostForAdmin,
  resolveDeviceConflictForAdmin,
  revokeRegisteredDeviceForAdmin,
  updateRegisteredDeviceForAdmin,
  type RegisteredDeviceAdminRowDto,
} from '../../api/admin-registered-devices-client';
import { listSitesForAdmin, type SiteAdminRowDto } from '../../api/admin-sites-client';
import { KPI_LIVE_BANNER_MODULE_KEY } from '../../api/module-config-client';
import { recycliqueClientFailureFromSalesHttp } from '../../api/recyclique-api-error';
import { useAuthPort } from '../../app/auth/AuthRuntimeProvider';
import type { RegisteredWidgetProps } from '../../registry/widget-registry';
import { CashflowClientErrorAlert } from '../cashflow/CashflowClientErrorAlert';
import type { CashflowSubmitSurfaceError } from '../cashflow/cashflow-submit-error';
import { ADMIN_SUPER_PAGE_MANIFEST_GUARDS } from './admin-super-page-guards';

const ACTIVE_MODULE_KEY_OPTIONS = [{ value: KPI_LIVE_BANNER_MODULE_KEY, label: KPI_LIVE_BANNER_MODULE_KEY }];

const STATUS_LABELS: Record<string, string> = {
  pending_enrollment: 'En attente d’enrôlement',
  active: 'Actif',
  identity_lost: 'Identité locale perdue',
  conflict: 'Conflit d’identité',
  revoked: 'Révoqué',
};

const STATUS_FILTER_OPTIONS = [
  { value: '', label: 'Tous les statuts' },
  { value: 'active', label: STATUS_LABELS.active },
  { value: 'pending_enrollment', label: STATUS_LABELS.pending_enrollment },
  { value: 'identity_lost', label: STATUS_LABELS.identity_lost },
  { value: 'conflict', label: STATUS_LABELS.conflict },
];

function statusBadgeColor(status: string): string {
  switch (status) {
    case 'active':
      return 'green';
    case 'pending_enrollment':
      return 'yellow';
    case 'revoked':
      return 'red';
    case 'identity_lost':
    case 'conflict':
      return 'orange';
    default:
      return 'gray';
  }
}

function formatTimeout(seconds: number | null | undefined): string {
  if (seconds == null) return '15 min (défaut serveur)';
  const min = Math.round(seconds / 60);
  return `${min} min`;
}

function formatLastContact(iso: string | null | undefined): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('fr-FR');
  } catch {
    return iso;
  }
}

function modulesSummary(keys: readonly string[]): string {
  if (!keys.length) return '—';
  if (keys.length <= 2) return keys.join(', ');
  return `${keys.slice(0, 2).join(', ')} (+${keys.length - 2})`;
}

/**
 * Postes partagés enrôlés — panel SuperAdmin (distinct des postes de caisse).
 */
export function AdminRegisteredDevicesWidget(_: RegisteredWidgetProps): ReactNode {
  const auth = useAuthPort();
  const envelope = auth.getContextEnvelope();
  const isSuperAdminUi = ADMIN_SUPER_PAGE_MANIFEST_GUARDS.requiredPermissionKeys.every((key) =>
    envelope.permissions.permissionKeys.includes(key),
  );

  const [rows, setRows] = useState<readonly RegisteredDeviceAdminRowDto[]>([]);
  const [sites, setSites] = useState<readonly SiteAdminRowDto[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<CashflowSubmitSurfaceError | null>(null);
  const [filterSiteId, setFilterSiteId] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [includeRevoked, setIncludeRevoked] = useState(false);

  const [createOpen, setCreateOpen] = useState(false);
  const [createName, setCreateName] = useState('');
  const [createSiteId, setCreateSiteId] = useState<string | null>(null);
  const [createLocation, setCreateLocation] = useState('');
  const [createModules, setCreateModules] = useState<string[]>([]);
  const [createTimeout, setCreateTimeout] = useState<string>('');
  const [createBusy, setCreateBusy] = useState(false);

  const [editTarget, setEditTarget] = useState<RegisteredDeviceAdminRowDto | null>(null);
  const [editName, setEditName] = useState('');
  const [editLocation, setEditLocation] = useState('');
  const [editSiteId, setEditSiteId] = useState<string | null>(null);
  const [editModules, setEditModules] = useState<string[]>([]);
  const [editTimeout, setEditTimeout] = useState<string>('');
  const [editBusy, setEditBusy] = useState(false);

  const [revokeTarget, setRevokeTarget] = useState<RegisteredDeviceAdminRowDto | null>(null);
  const [revokeReason, setRevokeReason] = useState('');
  const [revokeBusy, setRevokeBusy] = useState(false);

  const [codeModal, setCodeModal] = useState<{ code: string; expires_at: string; purpose: string } | null>(
    null,
  );
  const [codeBusy, setCodeBusy] = useState(false);
  const [conflictTarget, setConflictTarget] = useState<RegisteredDeviceAdminRowDto | null>(null);
  const [conflictDistinctName, setConflictDistinctName] = useState('');
  const [conflictBusy, setConflictBusy] = useState(false);

  const siteNameById = useMemo(() => {
    const m = new Map<string, string>();
    for (const s of sites) m.set(s.id, s.name);
    return m;
  }, [sites]);

  const siteSelectData = useMemo(
    () => sites.map((s) => ({ value: s.id, label: s.name })),
    [sites],
  );

  const filterSiteData = useMemo(
    () => [{ value: '', label: 'Tous les sites' }, ...siteSelectData],
    [siteSelectData],
  );

  const load = useCallback(async () => {
    if (!isSuperAdminUi) return;
    setBusy(true);
    setError(null);
    const listQuery = {
      limit: 200,
      site_id: filterSiteId && filterSiteId !== '' ? filterSiteId : null,
      status: filterStatus && filterStatus !== '' ? filterStatus : null,
      include_revoked: includeRevoked,
    };
    const [devRes, siteRes] = await Promise.all([
      listRegisteredDevicesForAdmin(auth, listQuery),
      listSitesForAdmin(auth, { limit: 200 }),
    ]);
    if (!devRes.ok) {
      setRows([]);
      setSites([]);
      setError({ kind: 'api', failure: recycliqueClientFailureFromSalesHttp(devRes) });
      setBusy(false);
      return;
    }
    setRows(devRes.data);
    setSites(siteRes.ok ? siteRes.data : []);
    if (!siteRes.ok) {
      setError({ kind: 'api', failure: recycliqueClientFailureFromSalesHttp(siteRes) });
    }
    setBusy(false);
  }, [auth, filterSiteId, filterStatus, includeRevoked, isSuperAdminUi]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (createOpen && sites.length === 1 && !createSiteId) {
      setCreateSiteId(sites[0].id);
    }
  }, [createOpen, sites, createSiteId]);

  const openEdit = (row: RegisteredDeviceAdminRowDto) => {
    setEditTarget(row);
    setEditName(row.name);
    setEditLocation(row.location ?? '');
    setEditSiteId(row.site_id);
    setEditModules([...row.allowed_module_keys]);
    setEditTimeout(
      row.inactivity_timeout_seconds != null ? String(row.inactivity_timeout_seconds) : '',
    );
  };

  const onCreate = async () => {
    const name = createName.trim();
    if (!name || !createSiteId) return;
    setCreateBusy(true);
    setError(null);
    const timeoutRaw = createTimeout.trim();
    const body = {
      name,
      site_id: createSiteId,
      location: createLocation.trim() || null,
      device_type: 'shared_workstation' as const,
      allowed_module_keys: createModules,
      ...(timeoutRaw ? { inactivity_timeout_seconds: Number(timeoutRaw) } : {}),
    };
    const res = await createRegisteredDeviceForAdmin(auth, body);
    setCreateBusy(false);
    if (!res.ok) {
      setError({ kind: 'api', failure: recycliqueClientFailureFromSalesHttp(res) });
      return;
    }
    setCreateOpen(false);
    setCreateName('');
    setCreateSiteId(null);
    setCreateLocation('');
    setCreateModules([]);
    setCreateTimeout('');
    await load();
  };

  const onSaveEdit = async () => {
    if (!editTarget) return;
    const name = editName.trim();
    if (!name || !editSiteId) return;
    setEditBusy(true);
    setError(null);
    const timeoutRaw = editTimeout.trim();
    const patch = {
      name,
      site_id: editSiteId,
      location: editLocation.trim() || null,
      allowed_module_keys: editModules,
      ...(timeoutRaw ? { inactivity_timeout_seconds: Number(timeoutRaw) } : {}),
    };
    const res = await updateRegisteredDeviceForAdmin(auth, editTarget.device_id, patch);
    setEditBusy(false);
    if (!res.ok) {
      setError({ kind: 'api', failure: recycliqueClientFailureFromSalesHttp(res) });
      return;
    }
    setEditTarget(null);
    await load();
  };

  const onConfirmRevoke = async () => {
    if (!revokeTarget) return;
    setRevokeBusy(true);
    setError(null);
    const res = await revokeRegisteredDeviceForAdmin(auth, revokeTarget.device_id, {
      reason: revokeReason.trim() || undefined,
    });
    setRevokeBusy(false);
    if (!res.ok) {
      setError({ kind: 'api', failure: recycliqueClientFailureFromSalesHttp(res) });
      return;
    }
    setRevokeTarget(null);
    setRevokeReason('');
    await load();
  };

  const onIssueCode = async (
    row: RegisteredDeviceAdminRowDto,
    purpose: 'initial_enrollment' | 'reconnect' | 'replace',
  ) => {
    setCodeBusy(true);
    setError(null);
    const res = await issueDeviceEnrollmentCodeForAdmin(auth, row.device_id, { purpose });
    setCodeBusy(false);
    if (!res.ok) {
      setError({ kind: 'api', failure: recycliqueClientFailureFromSalesHttp(res) });
      return;
    }
    setCodeModal({ code: res.code, expires_at: res.expires_at, purpose: res.purpose });
  };

  const onMarkIdentityLost = async (row: RegisteredDeviceAdminRowDto) => {
    setCodeBusy(true);
    setError(null);
    const res = await markDeviceIdentityLostForAdmin(auth, row.device_id);
    setCodeBusy(false);
    if (!res.ok) {
      setError({ kind: 'api', failure: recycliqueClientFailureFromSalesHttp(res) });
      return;
    }
    await load();
  };

  const onResolveConflict = async (action: 'refuse' | 'replace_definitively' | 'create_distinct') => {
    if (!conflictTarget) return;
    setConflictBusy(true);
    setError(null);
    const res = await resolveDeviceConflictForAdmin(auth, conflictTarget.device_id, {
      action,
      name: action === 'create_distinct' ? conflictDistinctName.trim() : undefined,
    });
    setConflictBusy(false);
    if (!res.ok) {
      setError({ kind: 'api', failure: recycliqueClientFailureFromSalesHttp(res) });
      return;
    }
    if (
      action === 'replace_definitively' &&
      res.enrollment_code &&
      res.enrollment_code_expires_at
    ) {
      setCodeModal({
        code: res.enrollment_code,
        expires_at: res.enrollment_code_expires_at,
        purpose: res.enrollment_code_purpose ?? 'replace',
      });
    }
    setConflictTarget(null);
    setConflictDistinctName('');
    await load();
  };

  if (!isSuperAdminUi) {
    return (
      <Stack gap="md" data-testid="widget-admin-registered-devices">
        <Title order={1}>Gestion des postes</Title>
        <Text size="sm" c="dimmed">
          Réservé au super-admin — accès refusé selon l’enveloppe de contexte.
        </Text>
      </Stack>
    );
  }

  return (
    <Stack gap="md" data-testid="widget-admin-registered-devices" aria-busy={busy}>
      <Group justify="space-between" align="flex-start" wrap="wrap">
        <div>
          <Title order={1}>Gestion des postes</Title>
          <Text size="sm" c="dimmed" mt={4}>
            Postes partagés enrôlés (identifiant <strong>device_id</strong>) — distincts des postes de
            caisse. Configuration serveur uniquement ; pas d’enrôlement terrain depuis cet écran.
          </Text>
        </div>
        <Group gap="sm">
          <Button
            variant="default"
            leftSection={<RefreshCw size={16} />}
            onClick={() => void load()}
            loading={busy}
            data-testid="admin-registered-devices-refresh"
          >
            Actualiser
          </Button>
          <Button onClick={() => setCreateOpen(true)} disabled={busy} data-testid="admin-registered-devices-create">
            Nouveau poste
          </Button>
        </Group>
      </Group>

      <Group gap="md" wrap="wrap">
        <Select
          label="Site"
          data={filterSiteData}
          value={filterSiteId ?? ''}
          onChange={(v) => setFilterSiteId(v === '' || v === null ? null : v)}
          w={220}
        />
        <Select
          label="Statut"
          data={STATUS_FILTER_OPTIONS}
          value={filterStatus}
          onChange={(v) => setFilterStatus(v ?? '')}
          w={220}
        />
        <Select
          label="Révoqués"
          data={[
            { value: 'false', label: 'Masquer révoqués' },
            { value: 'true', label: 'Inclure révoqués' },
          ]}
          value={includeRevoked ? 'true' : 'false'}
          onChange={(v) => setIncludeRevoked(v === 'true')}
          w={200}
        />
      </Group>

      {error ? <CashflowClientErrorAlert error={error} /> : null}

      <Paper withBorder p={0}>
        <Table striped highlightOnHover verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Nom</Table.Th>
              <Table.Th>Site</Table.Th>
              <Table.Th>Emplacement</Table.Th>
              <Table.Th>Statut</Table.Th>
              <Table.Th>Identifiant poste (device_id)</Table.Th>
              <Table.Th>Modules</Table.Th>
              <Table.Th>Timeout</Table.Th>
              <Table.Th>Dernier contact</Table.Th>
              <Table.Th> </Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {rows.length === 0 && !busy ? (
              <Table.Tr>
                <Table.Td colSpan={9}>
                  <Text size="sm" c="dimmed" py="md" ta="center">
                    Aucun poste partagé renvoyé par le serveur.
                  </Text>
                </Table.Td>
              </Table.Tr>
            ) : null}
            {rows.map((r) => {
              const siteLabel = siteNameById.get(r.site_id) ?? r.site_id.slice(0, 8);
              const readOnlyStatus = r.status === 'identity_lost' || r.status === 'conflict';
              const isRevoked = r.status === 'revoked';
              return (
                <Table.Tr key={r.device_id}>
                  <Table.Td>
                    <Text size="sm" fw={500}>
                      {r.name}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{siteLabel}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{r.location ?? '—'}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge color={statusBadgeColor(r.status)} variant="light">
                      {STATUS_LABELS[r.status] ?? r.status}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" ff="monospace" title={r.device_id}>
                      {r.device_id}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{modulesSummary(r.allowed_module_keys)}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{formatTimeout(r.inactivity_timeout_seconds)}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{formatLastContact(r.last_contact_at)}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs" wrap="wrap">
                      {r.status === 'pending_enrollment' ? (
                        <Button
                          size="xs"
                          variant="light"
                          loading={codeBusy}
                          data-testid="admin-registered-devices-issue-enrollment-code"
                          onClick={() => void onIssueCode(r, 'initial_enrollment')}
                        >
                          Code enrôlement
                        </Button>
                      ) : null}
                      {r.status === 'identity_lost' ? (
                        <Button
                          size="xs"
                          variant="light"
                          loading={codeBusy}
                          data-testid="admin-registered-devices-reconnect-code"
                          onClick={() => void onIssueCode(r, 'reconnect')}
                        >
                          Reconnecter
                        </Button>
                      ) : null}
                      {r.status === 'active' ? (
                        <>
                          <Button
                            size="xs"
                            variant="light"
                            loading={codeBusy}
                            data-testid="admin-registered-devices-replace-code"
                            onClick={() => void onIssueCode(r, 'replace')}
                          >
                            Remplacer
                          </Button>
                          <Button
                            size="xs"
                            variant="subtle"
                            loading={codeBusy}
                            data-testid="admin-registered-devices-mark-identity-lost"
                            onClick={() => void onMarkIdentityLost(r)}
                          >
                            Identité perdue
                          </Button>
                        </>
                      ) : null}
                      {r.status === 'conflict' ? (
                        <Button
                          size="xs"
                          variant="light"
                          color="orange"
                          data-testid="admin-registered-devices-resolve-conflict"
                          onClick={() => setConflictTarget(r)}
                        >
                          Résoudre conflit
                        </Button>
                      ) : null}
                      <Button
                        size="xs"
                        variant="light"
                        onClick={() => openEdit(r)}
                        disabled={isRevoked || readOnlyStatus}
                      >
                        Modifier
                      </Button>
                      <Button
                        size="xs"
                        variant="light"
                        color="red"
                        onClick={() => setRevokeTarget(r)}
                        disabled={isRevoked}
                        data-testid="admin-registered-devices-revoke"
                      >
                        Révoquer
                      </Button>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              );
            })}
          </Table.Tbody>
        </Table>
      </Paper>

      <Modal opened={createOpen} onClose={() => setCreateOpen(false)} title="Nouveau poste partagé">
        <Stack gap="sm">
          <TextInput
            label="Nom"
            required
            value={createName}
            onChange={(e) => setCreateName(e.currentTarget.value)}
            data-testid="admin-registered-devices-create-name"
          />
          <Select
            label="Site"
            required
            data={siteSelectData}
            value={createSiteId}
            onChange={setCreateSiteId}
            searchable
            data-testid="admin-registered-devices-create-site"
          />
          <TextInput
            label="Emplacement"
            value={createLocation}
            onChange={(e) => setCreateLocation(e.currentTarget.value)}
          />
          <TextInput label="Type" value="shared_workstation" readOnly disabled />
          <MultiSelect
            label="Modules autorisés"
            data={ACTIVE_MODULE_KEY_OPTIONS}
            value={createModules}
            onChange={setCreateModules}
          />
          <NumberInput
            label="Timeout inactivité (secondes, optionnel)"
            value={createTimeout === '' ? '' : Number(createTimeout)}
            onChange={(v) => setCreateTimeout(v === '' || v == null ? '' : String(v))}
            min={1}
          />
          <Group justify="flex-end" mt="md">
            <Button variant="default" onClick={() => setCreateOpen(false)}>
              Annuler
            </Button>
            <Button
              onClick={() => void onCreate()}
              loading={createBusy}
              disabled={!createName.trim() || !createSiteId}
              data-testid="admin-registered-devices-create-submit"
            >
              Créer
            </Button>
          </Group>
        </Stack>
      </Modal>

      <Modal opened={editTarget !== null} onClose={() => setEditTarget(null)} title="Modifier le poste">
        {editTarget ? (
          <Stack gap="sm">
            <TextInput
              label="Nom"
              required
              value={editName}
              onChange={(e) => setEditName(e.currentTarget.value)}
              data-testid="admin-registered-devices-edit-name"
            />
            <Select
              label="Site"
              required
              data={siteSelectData}
              value={editSiteId}
              onChange={setEditSiteId}
              searchable
            />
            <TextInput
              label="Emplacement"
              value={editLocation}
              onChange={(e) => setEditLocation(e.currentTarget.value)}
            />
            <MultiSelect
              label="Modules autorisés"
              data={ACTIVE_MODULE_KEY_OPTIONS}
              value={editModules}
              onChange={setEditModules}
            />
            <NumberInput
              label="Timeout inactivité (secondes, optionnel)"
              value={editTimeout === '' ? '' : Number(editTimeout)}
              onChange={(v) => setEditTimeout(v === '' || v == null ? '' : String(v))}
              min={1}
            />
            <Group justify="flex-end" mt="md">
              <Button variant="default" onClick={() => setEditTarget(null)}>
                Annuler
              </Button>
              <Button
                onClick={() => void onSaveEdit()}
                loading={editBusy}
                disabled={!editName.trim() || !editSiteId}
                data-testid="admin-registered-devices-edit-submit"
              >
                Enregistrer
              </Button>
            </Group>
          </Stack>
        ) : null}
      </Modal>

      <Modal
        opened={revokeTarget !== null}
        onClose={() => setRevokeTarget(null)}
        title="Révoquer le poste ?"
      >
        {revokeTarget ? (
          <Stack gap="sm">
            <Text size="sm">
              Le poste « {revokeTarget.name} » ({revokeTarget.device_id}) sera révoqué. Les sessions
              opérateur actives seront invalidées côté serveur.
            </Text>
            <TextInput
              label="Motif (optionnel)"
              value={revokeReason}
              onChange={(e) => setRevokeReason(e.currentTarget.value)}
            />
            <Group justify="flex-end" mt="md">
              <Button variant="default" onClick={() => setRevokeTarget(null)}>
                Annuler
              </Button>
              <Button
                color="red"
                onClick={() => void onConfirmRevoke()}
                loading={revokeBusy}
                data-testid="admin-registered-devices-revoke-confirm"
              >
                Révoquer
              </Button>
            </Group>
          </Stack>
        ) : null}
      </Modal>

      <Modal opened={codeModal !== null} onClose={() => setCodeModal(null)} title="Code d'enrôlement">
        {codeModal ? (
          <Stack gap="sm">
            <Text size="sm">
              Code à saisir sur le poste (usage unique, ~15 min). Copiez-le maintenant — il ne sera plus affiché.
            </Text>
            <Text ff="monospace" fw={700} size="xl" data-testid="admin-registered-devices-code-display">
              {codeModal.code}
            </Text>
            <Text size="sm" c="dimmed">
              Expire : {codeModal.expires_at ? new Date(codeModal.expires_at).toLocaleString('fr-FR') : '—'}
            </Text>
            <Group justify="flex-end">
              <Button
                onClick={() => {
                  void navigator.clipboard?.writeText(codeModal.code);
                }}
              >
                Copier
              </Button>
              <Button variant="default" onClick={() => setCodeModal(null)}>
                Fermer
              </Button>
            </Group>
          </Stack>
        ) : null}
      </Modal>

      <Modal
        opened={conflictTarget !== null}
        onClose={() => setConflictTarget(null)}
        title="Résoudre le conflit d'identité"
      >
        {conflictTarget ? (
          <Stack gap="sm">
            <Text size="sm">
              Poste « {conflictTarget.name} » — choisissez une action explicite. L'ancienne machine restera
              bloquée sauf remplacement ou nouveau poste distinct.
            </Text>
            <Button
              variant="light"
              loading={conflictBusy}
              onClick={() => void onResolveConflict('refuse')}
            >
              Refuser l'ancienne machine (garder le credential actuel)
            </Button>
            <Button
              variant="light"
              loading={conflictBusy}
              onClick={() => void onResolveConflict('replace_definitively')}
            >
              Remplacer définitivement (rotation forcée)
            </Button>
            <TextInput
              label="Nom du nouveau poste distinct"
              value={conflictDistinctName}
              onChange={(e) => setConflictDistinctName(e.currentTarget.value)}
            />
            <Button
              variant="light"
              loading={conflictBusy}
              disabled={!conflictDistinctName.trim()}
              onClick={() => void onResolveConflict('create_distinct')}
            >
              Créer un poste distinct pour l'ancienne machine
            </Button>
          </Stack>
        ) : null}
      </Modal>
    </Stack>
  );
}
