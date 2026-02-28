/**
 * Page admin Permissions — Story 11.6.
 * Route : /admin/permissions. GET/POST/PUT/DELETE /v1/admin/permissions. Rendu Mantine 1.4.4.
 */
import { useCallback, useEffect, useState } from 'react';
import {
  Stack,
  Title,
  Text,
  Card,
  Alert,
  Loader,
  Table,
  Group,
  Button,
  Modal,
  TextInput,
  ActionIcon,
} from '@mantine/core';
import { useAuth } from '../auth/AuthContext';
import {
  getAdminPermissions,
  createAdminPermission,
  updateAdminPermission,
  deleteAdminPermission,
  type AdminPermission,
} from '../api/adminPermissions';

export function AdminPermissionsPage() {
  const { accessToken, permissions } = useAuth();
  const [list, setList] = useState<AdminPermission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [code, setCode] = useState('');
  const [label, setLabel] = useState('');
  const [saveLoading, setSaveLoading] = useState(false);

  const canAccess = permissions.includes('admin') || permissions.includes('super_admin');

  const load = useCallback(async () => {
    if (!accessToken || !canAccess) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getAdminPermissions(accessToken);
      setList(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur chargement');
    } finally {
      setLoading(false);
    }
  }, [accessToken, canAccess]);

  useEffect(() => {
    load();
  }, [load]);

  const openCreate = () => {
    setEditingId(null);
    setCode('');
    setLabel('');
    setModalOpen(true);
  };

  const openEdit = (p: AdminPermission) => {
    setEditingId(p.id);
    setCode(p.code);
    setLabel(p.label ?? '');
    setModalOpen(true);
  };

  const handleSave = async () => {
    if (!accessToken || !code.trim()) return;
    setSaveLoading(true);
    setError(null);
    try {
      if (editingId) {
        await updateAdminPermission(accessToken, editingId, { code: code.trim(), label: label.trim() || null });
      } else {
        await createAdminPermission(accessToken, { code: code.trim(), label: label.trim() || null });
      }
      setModalOpen(false);
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur enregistrement');
    } finally {
      setSaveLoading(false);
    }
  };

  const handleDelete = async (p: AdminPermission) => {
    if (!accessToken || !window.confirm(`Supprimer la permission « ${p.code} » ?`)) return;
    setError(null);
    try {
      await deleteAdminPermission(accessToken, p.id);
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur suppression');
    }
  };

  if (!canAccess) {
    return (
      <div data-testid="admin-permissions-forbidden">
        <Text>Accès réservé aux administrateurs.</Text>
      </div>
    );
  }

  return (
    <Stack gap="md" data-testid="admin-permissions-page">
      <Title order={2}>Permissions</Title>
      <Text size="sm" c="dimmed" mb="xs">
        Gestion des permissions et liaison aux groupes (§7.11).
      </Text>
      {error && <Alert color="red">{error}</Alert>}

      <Card withBorder padding="md" radius="md">
        <Group justify="space-between" mb="md">
          <Text fw={500}>Liste des permissions</Text>
          <Button size="sm" onClick={openCreate} data-testid="admin-permissions-create">
            Créer une permission
          </Button>
        </Group>
        {loading ? (
          <Loader size="sm" data-testid="admin-permissions-loading" />
        ) : (
          <Table striped highlightOnHover data-testid="admin-permissions-table">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Code</Table.Th>
                <Table.Th>Libellé</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {list.map((p) => (
                <Table.Tr key={p.id} data-testid={`permission-row-${p.id}`}>
                  <Table.Td>{p.code}</Table.Td>
                  <Table.Td>{p.label ?? '—'}</Table.Td>
                  <Table.Td>
                    <Group gap="xs">
                      <Button
                        variant="light"
                        size="xs"
                        onClick={() => openEdit(p)}
                        data-testid={`permission-edit-${p.id}`}
                      >
                        Modifier
                      </Button>
                      <ActionIcon
                        variant="light"
                        color="red"
                        size="sm"
                        onClick={() => handleDelete(p)}
                        data-testid={`permission-delete-${p.id}`}
                        aria-label="Supprimer"
                      >
                        —
                      </ActionIcon>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
        {list.length === 0 && !loading && (
          <Text size="sm" c="dimmed" data-testid="admin-permissions-empty">
            Aucune permission.
          </Text>
        )}
      </Card>

      <Modal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingId ? 'Modifier la permission' : 'Nouvelle permission'}
        data-testid="modal-permission-form"
      >
        <Stack gap="sm">
          <TextInput
            label="Code"
            value={code}
            onChange={(e) => setCode(e.currentTarget.value)}
            data-testid="input-permission-code"
            required
          />
          <TextInput
            label="Libellé"
            value={label}
            onChange={(e) => setLabel(e.currentTarget.value)}
            data-testid="input-permission-label"
          />
          <Group>
            <Button loading={saveLoading} onClick={handleSave} disabled={!code.trim()} data-testid="btn-permission-save">
              Enregistrer
            </Button>
            <Button variant="subtle" onClick={() => setModalOpen(false)}>
              Annuler
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
}
