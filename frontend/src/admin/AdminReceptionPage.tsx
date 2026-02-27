/**
 * Page admin Réception — Story 8.4.
 * Route : /admin/reception. Stats, liste tickets, lien détail (APIs Epic 6).
 */
import React, { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Stack,
  Group,
  Title,
  Alert,
  Loader,
  Table,
  Button,
  Card,
  Text,
  Select,
  Tabs,
} from '@mantine/core';
import { useAuth } from '../auth/AuthContext';
import {
  getReceptionStatsLive,
  getTickets,
  type TicketDepotItem,
  type ReceptionStatsLive,
} from '../api/reception';
import { postAdminReceptionTicketsExportBulk } from '../api/adminHealthAudit';

const PAGE_SIZE = 20;

export function AdminReceptionPage() {
  const { accessToken, permissions } = useAuth();
  const [stats, setStats] = useState<ReceptionStatsLive | null>(null);
  const [tickets, setTickets] = useState<TicketDepotItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exportBulkLoading, setExportBulkLoading] = useState(false);

  const loadStats = useCallback(async () => {
    if (!accessToken || !permissions.includes('admin')) return;
    try {
      const data = await getReceptionStatsLive(accessToken);
      setStats(data);
    } catch {
      setStats(null);
    }
  }, [accessToken, permissions]);

  const loadTickets = useCallback(async () => {
    if (!accessToken || !permissions.includes('admin')) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getTickets(accessToken, {
        page,
        page_size: PAGE_SIZE,
        status: statusFilter || undefined,
      });
      setTickets(data.items);
      setTotal(data.total);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur chargement');
    } finally {
      setLoading(false);
    }
  }, [accessToken, permissions, page, statusFilter]);

  const handleExportBulk = useCallback(async () => {
    if (!accessToken) return;
    setExportBulkLoading(true);
    setError(null);
    try {
      await postAdminReceptionTicketsExportBulk(accessToken, {
        status: statusFilter ?? undefined,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur export');
    } finally {
      setExportBulkLoading(false);
    }
  }, [accessToken, statusFilter]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  if (!permissions.includes('admin')) {
    return (
      <div data-testid="admin-reception-forbidden">
        <p>Accès réservé aux administrateurs.</p>
      </div>
    );
  }

  return (
    <Stack gap="md" data-testid="admin-reception-page">
      <Title order={2}>Admin réception</Title>

      <Tabs defaultValue="stats">
        <Tabs.List>
          <Tabs.Tab value="stats">Stats</Tabs.Tab>
          <Tabs.Tab value="tickets">Tickets</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="stats">
          {stats === null ? (
            <Loader size="sm" data-testid="admin-reception-stats-loading" />
          ) : (
            <Group gap="md" mt="md">
              <Card shadow="sm" padding="md" withBorder>
                <Text size="sm" c="dimmed">Tickets aujourd&apos;hui</Text>
                <Text fw={700} size="xl" data-testid="admin-reception-tickets-today">
                  {stats?.tickets_today ?? 0}
                </Text>
              </Card>
              <Card shadow="sm" padding="md" withBorder>
                <Text size="sm" c="dimmed">Poids total (kg)</Text>
                <Text fw={700} size="xl" data-testid="admin-reception-weight">
                  {stats?.total_weight_kg ?? 0}
                </Text>
              </Card>
              <Card shadow="sm" padding="md" withBorder>
                <Text size="sm" c="dimmed">Lignes aujourd&apos;hui</Text>
                <Text fw={700} size="xl" data-testid="admin-reception-lines">
                  {stats?.lines_count ?? 0}
                </Text>
              </Card>
            </Group>
          )}
        </Tabs.Panel>

        <Tabs.Panel value="tickets">
          <Group gap="sm" mt="md">
            <Select
              placeholder="Statut"
              clearable
              data={[
                { value: 'opened', label: 'Ouvert' },
                { value: 'closed', label: 'Fermé' },
              ]}
              value={statusFilter}
              onChange={setStatusFilter}
              data-testid="filter-status"
            />
            <Button variant="subtle" onClick={() => { setStatusFilter(null); setPage(1); loadTickets(); }}>
              Réinitialiser
            </Button>
            <Button
              variant="light"
              loading={exportBulkLoading}
              onClick={handleExportBulk}
              data-testid="btn-export-bulk-reception"
            >
              Export bulk tickets réception
            </Button>
          </Group>
          {error && <Alert color="red">{error}</Alert>}
          {loading ? (
            <Loader size="sm" data-testid="admin-reception-tickets-loading" />
          ) : (
            <>
              <Table striped highlightOnHover data-testid="admin-reception-tickets-table">
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>ID</Table.Th>
                    <Table.Th>Créé</Table.Th>
                    <Table.Th>Statut</Table.Th>
                    <Table.Th>Actions</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {tickets.map((t) => (
                    <Table.Tr key={t.id}>
                      <Table.Td>{t.id.slice(0, 8)}</Table.Td>
                      <Table.Td>{new Date(t.created_at).toLocaleString()}</Table.Td>
                      <Table.Td>{t.status}</Table.Td>
                      <Table.Td>
                        <Button
                          component={Link}
                          to={`/admin/reception-tickets/${t.id}`}
                          variant="light"
                          size="xs"
                          data-testid={`link-ticket-${t.id}`}
                        >
                          Détail
                        </Button>
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
              {tickets.length === 0 && (
                <p data-testid="admin-reception-tickets-empty">Aucun ticket.</p>
              )}
              {total > PAGE_SIZE && (
                <Group gap="sm" data-testid="admin-reception-pagination">
                  <Button
                    variant="subtle"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                  >
                    Précédent
                  </Button>
                  <Text size="sm">Page {page} / {Math.ceil(total / PAGE_SIZE) || 1}</Text>
                  <Button
                    variant="subtle"
                    size="sm"
                    disabled={page * PAGE_SIZE >= total}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Suivant
                  </Button>
                </Group>
              )}
            </>
          )}
        </Tabs.Panel>
      </Tabs>
    </Stack>
  );
}
