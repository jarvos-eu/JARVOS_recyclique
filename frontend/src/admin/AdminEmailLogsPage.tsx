/**
 * Page admin Logs email — Story 8.4.
 * Route : /admin/email-logs. GET /v1/admin/email-logs (stub v1, lecture seule).
 */
import React, { useCallback, useEffect, useState } from 'react';
import { Stack, Title, Alert, Loader, Table, Text } from '@mantine/core';
import { useAuth } from '../auth/AuthContext';
import { getAdminEmailLogs, type EmailLogItem } from '../api/adminHealthAudit';

const PAGE_SIZE = 20;

export function AdminEmailLogsPage() {
  const { accessToken, permissions } = useAuth();
  const [items, setItems] = useState<EmailLogItem[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!accessToken || !permissions.includes('admin')) return;
    setLoading(true);
    setError(null);
    try {
      const res = await getAdminEmailLogs(accessToken, { page, page_size: PAGE_SIZE });
      setItems(res.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur chargement');
    } finally {
      setLoading(false);
    }
  }, [accessToken, permissions, page]);

  useEffect(() => {
    load();
  }, [load]);

  if (!permissions.includes('admin')) {
    return (
      <div data-testid="admin-email-logs-forbidden">
        <p>Accès réservé aux administrateurs.</p>
      </div>
    );
  }

  return (
    <Stack gap="md" data-testid="admin-email-logs-page">
      <Title order={2}>Logs email</Title>
      <Text size="sm" c="dimmed">
        Consultation des envois email (stub v1 : liste vide si non implémenté).
      </Text>
      {error && <Alert color="red">{error}</Alert>}
      {loading ? (
        <Loader size="sm" data-testid="admin-email-logs-loading" />
      ) : (
        <>
          <Table striped highlightOnHover data-testid="admin-email-logs-table">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Date</Table.Th>
                <Table.Th>Destinataire</Table.Th>
                <Table.Th>Sujet</Table.Th>
                <Table.Th>Statut</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {items.map((log) => (
                <Table.Tr key={log.id}>
                  <Table.Td>{new Date(log.sent_at).toLocaleString()}</Table.Td>
                  <Table.Td>{log.recipient}</Table.Td>
                  <Table.Td>{log.subject}</Table.Td>
                  <Table.Td>{log.status}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
          {items.length === 0 && (
            <p data-testid="admin-email-logs-empty">Aucun log email.</p>
          )}
        </>
      )}
    </Stack>
  );
}
