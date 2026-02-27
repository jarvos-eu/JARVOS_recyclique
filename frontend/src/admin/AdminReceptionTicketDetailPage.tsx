/**
 * Page admin Réception — détail ticket — Story 8.4.
 * Route : /admin/reception-tickets/:id. GET /v1/reception/tickets/{id}.
 */
import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Stack, Title, Alert, Loader, Table, Button, Group } from '@mantine/core';
import { useAuth } from '../auth/AuthContext';
import { getTicket, type TicketDepotItem } from '../api/reception';

export function AdminReceptionTicketDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { accessToken, permissions } = useAuth();
  const [ticket, setTicket] = useState<TicketDepotItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id || !accessToken || !permissions.includes('admin')) return;
    setLoading(true);
    setError(null);
    getTicket(accessToken, id)
      .then(setTicket)
      .catch((e) => setError(e instanceof Error ? e.message : 'Erreur'))
      .finally(() => setLoading(false));
  }, [id, accessToken, permissions]);

  if (!permissions.includes('admin')) {
    return (
      <div data-testid="admin-reception-ticket-forbidden">
        <p>Accès réservé aux administrateurs.</p>
      </div>
    );
  }

  if (loading) {
    return <Loader size="sm" data-testid="admin-reception-ticket-loading" />;
  }
  if (error || !ticket) {
    return (
      <Stack gap="md">
        {error && <Alert color="red">{error}</Alert>}
        <Button component={Link} to="/admin/reception">Retour à la liste</Button>
      </Stack>
    );
  }

  const lignes = ticket.lignes ?? [];
  return (
    <Stack gap="md" data-testid="admin-reception-ticket-detail">
      <Group justify="space-between">
        <Title order={2}>Ticket {ticket.id.slice(0, 8)}</Title>
        <Button component={Link} to="/admin/reception" variant="subtle" size="sm">
          Retour à la liste
        </Button>
      </Group>
      <p>
        <strong>Créé :</strong> {new Date(ticket.created_at).toLocaleString()} —
        <strong> Statut :</strong> {ticket.status}
      </p>
      <Title order={3}>Lignes</Title>
      <Table striped highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Catégorie</Table.Th>
            <Table.Th>Poids (kg)</Table.Th>
            <Table.Th>Destination</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {lignes.map((l) => (
            <Table.Tr key={l.id}>
              <Table.Td>{l.category_id ?? '—'}</Table.Td>
              <Table.Td>{l.poids_kg}</Table.Td>
              <Table.Td>{l.destination || '—'}</Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
      {lignes.length === 0 && <p>Aucune ligne.</p>}
    </Stack>
  );
}
