/**
 * Page admin Santé — Story 8.4, 11.5.
 * Route : /admin/health. GET /v1/admin/health, /health/database, /health/scheduler. Rendu Mantine 1.4.4.
 */
import { useCallback, useEffect, useState } from 'react';
import { Stack, Title, Alert, Loader, Card, Text, Group, Badge, Button, SimpleGrid } from '@mantine/core';
import { useAuth } from '../auth/AuthContext';
import {
  getAdminHealth,
  getAdminHealthDatabase,
  getAdminHealthScheduler,
  postAdminHealthTestNotifications,
  type AdminHealthResponse,
  type AdminHealthSchedulerResponse,
} from '../api/adminHealthAudit';

export function AdminHealthPage() {
  const { accessToken, permissions } = useAuth();
  const [health, setHealth] = useState<AdminHealthResponse | null>(null);
  const [dbStatus, setDbStatus] = useState<string | null>(null);
  const [scheduler, setScheduler] = useState<AdminHealthSchedulerResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testNotifLoading, setTestNotifLoading] = useState(false);
  const [testNotifMessage, setTestNotifMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!accessToken || !permissions.includes('admin')) return;
    setLoading(true);
    setError(null);
    try {
      const [h, db, s] = await Promise.all([
        getAdminHealth(accessToken),
        getAdminHealthDatabase(accessToken),
        getAdminHealthScheduler(accessToken),
      ]);
      setHealth(h);
      setDbStatus(db.status);
      setScheduler(s);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur chargement');
    } finally {
      setLoading(false);
    }
  }, [accessToken, permissions]);

  const handleTestNotifications = useCallback(async () => {
    if (!accessToken) return;
    setTestNotifLoading(true);
    setTestNotifMessage(null);
    setError(null);
    try {
      const data = await postAdminHealthTestNotifications(accessToken);
      setTestNotifMessage(data.message ?? 'OK');
    } catch (e) {
      setTestNotifMessage(e instanceof Error ? e.message : 'Erreur');
    } finally {
      setTestNotifLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    load();
  }, [load]);

  if (!permissions.includes('admin')) {
    return (
      <div data-testid="admin-health-forbidden">
        <p>Accès réservé aux administrateurs.</p>
      </div>
    );
  }

  if (loading) {
    return <Loader size="sm" data-testid="admin-health-loading" />;
  }
  if (error) {
    return (
      <Stack gap="md">
        <Title order={2}>Santé</Title>
        <Alert color="red">{error}</Alert>
      </Stack>
    );
  }

  const statusColor = (s: string) => (s === 'ok' ? 'green' : s === 'unconfigured' ? 'gray' : 'red');
  return (
    <Stack gap="md" data-testid="admin-health-page">
      <Title order={2}>Santé</Title>
      <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
        <Card withBorder padding="md" radius="md" shadow="sm">
          <Text size="sm" c="dimmed">Global</Text>
          <Badge color={statusColor(health?.status ?? '')} size="lg" data-testid="health-status">
            {health?.status ?? '—'}
          </Badge>
        </Card>
        <Card withBorder padding="md" radius="md" shadow="sm">
          <Text size="sm" c="dimmed">Base de données</Text>
          <Badge color={statusColor(health?.database ?? dbStatus ?? '')} data-testid="health-database">
            {health?.database ?? dbStatus ?? '—'}
          </Badge>
        </Card>
        <Card withBorder padding="md" radius="md" shadow="sm">
          <Text size="sm" c="dimmed">Redis</Text>
          <Badge color={statusColor(health?.redis ?? '')} data-testid="health-redis">
            {health?.redis ?? '—'}
          </Badge>
        </Card>
        <Card withBorder padding="md" radius="md" shadow="sm">
          <Text size="sm" c="dimmed">Scheduler (push worker)</Text>
          <Badge color={statusColor(scheduler?.status ?? '')} data-testid="health-scheduler">
            {scheduler?.status ?? '—'}
          </Badge>
          {scheduler && (
            <Text size="xs" mt="xs" c="dimmed">
              Configuré: {scheduler.configured ? 'oui' : 'non'} — Running: {scheduler.running ? 'oui' : 'non'}
            </Text>
          )}
        </Card>
      </SimpleGrid>
      <Group>
        <Button
          loading={testNotifLoading}
          onClick={handleTestNotifications}
          variant="light"
          data-testid="btn-test-notifications"
        >
          Test notifications
        </Button>
        {testNotifMessage && (
          <Text size="sm" c="dimmed" data-testid="test-notifications-message">
            {testNotifMessage}
          </Text>
        )}
      </Group>
    </Stack>
  );
}
