/**
 * Dashboard admin — Story 8.1, 8.2, 8.6, 11.4.
 * Stats agrégées (GET /v1/admin/dashboard/stats si dispo), liens vers sous-sections.
 * Rendu Mantine aligné 1.4.4 (Card, espacements, typo).
 */
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Stack, Title, Anchor, Card, Text, SimpleGrid } from '@mantine/core';
import { useAuth } from '../auth/AuthContext';
import { getPahekoComptaUrl } from '../api/adminPahekoCompta';
import { getDashboardStats } from '../api/adminDashboard';

const ADMIN_LINKS = [
  { to: '/admin/users', label: 'Utilisateurs' },
  { to: '/admin/sites', label: 'Sites' },
  { to: '/admin/cash-registers', label: 'Postes de caisse' },
  { to: '/admin/session-manager', label: 'Gestionnaire de sessions caisse' },
  { to: '/admin/reports', label: 'Rapports caisse' },
  { to: '/admin/categories', label: 'Catégories' },
  { to: '/admin/groups', label: 'Groupes' },
  { to: '/admin/permissions', label: 'Permissions' },
  { to: '/admin/reception', label: 'Réception (stats, tickets)' },
  { to: '/admin/health', label: 'Santé' },
  { to: '/admin/audit-log', label: 'Audit log' },
  { to: '/admin/email-logs', label: 'Logs email' },
  { to: '/admin/settings', label: 'Paramètres' },
  { to: '/admin/db', label: 'BDD (export, purge, import)' },
  { to: '/admin/import/legacy', label: 'Import legacy' },
  { to: '/admin/quick-analysis', label: 'Analyse rapide' },
] as const;

export function AdminDashboardPage() {
  const { permissions, accessToken } = useAuth();
  const isAdmin = permissions.includes('admin');
  const [pahekoComptaUrl, setPahekoComptaUrl] = useState<string | null>(null);
  const [stats, setStats] = useState<{ users_count?: number; sites_count?: number; cash_registers_count?: number; open_sessions_count?: number; pending_users_count?: number } | null>(null);

  const loadPahekoUrl = useCallback(async () => {
    if (!isAdmin || !accessToken) return;
    try {
      const data = await getPahekoComptaUrl(accessToken);
      setPahekoComptaUrl(data.url ?? null);
    } catch {
      setPahekoComptaUrl(null);
    }
  }, [isAdmin, accessToken]);

  const loadStats = useCallback(async () => {
    if (!isAdmin || !accessToken) return;
    try {
      const data = await getDashboardStats(accessToken);
      setStats(data ?? null);
    } catch {
      setStats(null);
    }
  }, [isAdmin, accessToken]);

  useEffect(() => {
    loadPahekoUrl();
  }, [loadPahekoUrl]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  return (
    <Stack gap="md" data-testid="page-admin">
      <Title order={1}>Admin</Title>
      {isAdmin && (
        <>
          {stats != null && (stats.users_count != null || stats.sites_count != null || stats.cash_registers_count != null || stats.open_sessions_count != null || stats.pending_users_count != null) && (
            <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }} spacing="md">
              {stats.users_count != null && (
                <Card withBorder padding="md" radius="md" data-testid="dashboard-stat-users">
                  <Text size="sm" c="dimmed">Utilisateurs</Text>
                  <Text fw={600} size="xl">{stats.users_count}</Text>
                </Card>
              )}
              {stats.sites_count != null && (
                <Card withBorder padding="md" radius="md" data-testid="dashboard-stat-sites">
                  <Text size="sm" c="dimmed">Sites</Text>
                  <Text fw={600} size="xl">{stats.sites_count}</Text>
                </Card>
              )}
              {stats.cash_registers_count != null && (
                <Card withBorder padding="md" radius="md" data-testid="dashboard-stat-registers">
                  <Text size="sm" c="dimmed">Postes de caisse</Text>
                  <Text fw={600} size="xl">{stats.cash_registers_count}</Text>
                </Card>
              )}
              {stats.open_sessions_count != null && (
                <Card withBorder padding="md" radius="md" data-testid="dashboard-stat-sessions">
                  <Text size="sm" c="dimmed">Sessions ouvertes</Text>
                  <Text fw={600} size="xl">{stats.open_sessions_count}</Text>
                </Card>
              )}
              {stats.pending_users_count != null && (
                <Card withBorder padding="md" radius="md" data-testid="dashboard-stat-pending">
                  <Text size="sm" c="dimmed">Inscriptions en attente</Text>
                  <Text fw={600} size="xl">{stats.pending_users_count}</Text>
                </Card>
              )}
            </SimpleGrid>
          )}
          <Card withBorder padding="md" radius="md">
            <Text size="sm" fw={500} mb="xs">Navigation</Text>
            <Stack gap="xs">
              {ADMIN_LINKS.map(({ to, label }) => (
                <p key={to}>
                  <Anchor component={Link} to={to}>
                    {label}
                  </Anchor>
                </p>
              ))}
              {pahekoComptaUrl && (
                <p>
                  <Anchor href={pahekoComptaUrl} target="_blank" rel="noopener noreferrer">
                    Comptabilité (Paheko)
                  </Anchor>
                </p>
              )}
            </Stack>
          </Card>
        </>
      )}
    </Stack>
  );
}
