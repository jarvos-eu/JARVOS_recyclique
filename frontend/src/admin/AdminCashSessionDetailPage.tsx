/**
 * Page admin Détail session caisse — Story 8.2 (écran 5.5).
 * Route : /admin/cash-sessions/:id. GET /v1/cash-sessions/{id}, lien rapport.
 */
import React, { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Stack, Title, Alert, Loader, Button, Group, Text } from '@mantine/core';
import { useAuth } from '../auth/AuthContext';
import { getCashSession, type CashSessionItem } from '../api/caisse';
import { getReportBySession } from '../api/adminReports';

export function AdminCashSessionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { accessToken, permissions } = useAuth();
  const [session, setSession] = useState<CashSessionItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSession = useCallback(async () => {
    if (!accessToken || !id || !permissions.includes('admin')) return;
    setLoading(true);
    setError(null);
    try {
      const s = await getCashSession(accessToken, id);
      setSession(s);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Session introuvable');
    } finally {
      setLoading(false);
    }
  }, [accessToken, id, permissions]);

  useEffect(() => {
    loadSession();
  }, [loadSession]);

  const handleDownloadReport = async () => {
    if (!accessToken || !id) return;
    setError(null);
    try {
      const blob = await getReportBySession(accessToken, id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rapport-session-${id}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur téléchargement');
    }
  };

  if (!permissions.includes('admin')) {
    return (
      <div data-testid="admin-session-detail-forbidden">
        <p>Accès réservé aux administrateurs.</p>
      </div>
    );
  }

  if (loading) return <Loader size="sm" data-testid="admin-session-detail-loading" />;
  if (error && !session) return <Alert color="red">{error}</Alert>;
  if (!session) return <p data-testid="admin-session-detail-not-found">Session introuvable.</p>;

  return (
    <Stack gap="md" data-testid="admin-session-detail-page">
      <Group justify="space-between">
        <Title order={2}>Session caisse {session.id.slice(0, 8)}</Title>
        <Button component={Link} to="/admin/session-manager" variant="subtle" size="sm">
          Retour liste
        </Button>
      </Group>

      {error && <Alert color="red">{error}</Alert>}

      <Stack gap="xs">
        <Text><strong>Ouverture :</strong> {new Date(session.opened_at).toLocaleString()}</Text>
        <Text><strong>Clôture :</strong> {session.closed_at ? new Date(session.closed_at).toLocaleString() : '—'}</Text>
        <Text><strong>Statut :</strong> {session.status}</Text>
        <Text><strong>Type :</strong> {session.session_type}</Text>
        <Text><strong>Fond de caisse :</strong> {(session.initial_amount / 100).toFixed(2)} €</Text>
        {session.closing_amount != null && <Text><strong>Montant clôture :</strong> {(session.closing_amount / 100).toFixed(2)} €</Text>}
        {session.total_sales != null && <Text><strong>Total ventes :</strong> {(session.total_sales / 100).toFixed(2)} €</Text>}
        {session.total_items != null && <Text><strong>Nombre d'articles :</strong> {session.total_items}</Text>}
      </Stack>

      {session.status === 'closed' && (
        <Button onClick={handleDownloadReport} data-testid="download-report">
          Télécharger le rapport
        </Button>
      )}
    </Stack>
  );
}
