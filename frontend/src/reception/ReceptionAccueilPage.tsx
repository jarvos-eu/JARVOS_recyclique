/**
 * Accueil réception — Story 6.1, 6.3.
 * État du poste (ouvert/fermé), boutons Ouvrir poste, Créer ticket, Fermer poste,
 * liste des tickets du poste courant. KPI live (stats/live), export lignes (période).
 * Alignement Mantine (architecture/checklist v0.1).
 */
import React, { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button, Modal, Stack, Title, Text, Group, List, TextInput, Anchor } from '@mantine/core';
import {
  getCurrentPoste,
  openPoste,
  closePoste,
  getTickets,
  createTicket,
  getReceptionStatsLive,
  exportLignesCsv,
} from '../api/reception';
import type { PosteReceptionItem, TicketDepotItem, ReceptionStatsLive } from '../api/reception';
import { useAuth } from '../auth/AuthContext';

export function ReceptionAccueilPage() {
  const { accessToken } = useAuth();
  const [poste, setPoste] = useState<PosteReceptionItem | null | undefined>(undefined);
  const [tickets, setTickets] = useState<TicketDepotItem[]>([]);
  const [totalTickets, setTotalTickets] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openModal, setOpenModal] = useState(false);
  const [openedAtValue, setOpenedAtValue] = useState('');
  const [stats, setStats] = useState<ReceptionStatsLive | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [exportLignesFrom, setExportLignesFrom] = useState('');
  const [exportLignesTo, setExportLignesTo] = useState('');
  const [exportLignesPending, setExportLignesPending] = useState(false);
  const [exportLignesModal, setExportLignesModal] = useState(false);

  const loadPoste = useCallback(async () => {
    if (!accessToken) return;
    setError(null);
    try {
      const p = await getCurrentPoste(accessToken);
      setPoste(p);
      return p;
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur chargement poste');
      setPoste(null);
      return null;
    }
  }, [accessToken]);

  const loadTickets = useCallback(
    async (posteId: string) => {
      if (!accessToken) return;
      try {
        const res = await getTickets(accessToken, { poste_id: posteId, page: 1, page_size: 50 });
        setTickets(res.items);
        setTotalTickets(res.total);
      } catch {
        setTickets([]);
        setTotalTickets(0);
      }
    },
    [accessToken]
  );

  useEffect(() => {
    if (!accessToken) return;
    setLoading(true);
    loadPoste().then((p) => {
      if (p?.id) loadTickets(p.id);
      setLoading(false);
    });
  }, [accessToken, loadPoste, loadTickets]);

  const loadStats = useCallback(async () => {
    if (!accessToken) return;
    setStatsLoading(true);
    try {
      const s = await getReceptionStatsLive(accessToken);
      setStats(s);
    } catch {
      setStats(null);
    } finally {
      setStatsLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    if (!accessToken) return;
    loadStats();
    const interval = setInterval(loadStats, 30_000);
    return () => clearInterval(interval);
  }, [accessToken, loadStats]);

  const handleExportLignes = useCallback(async () => {
    if (!accessToken || !exportLignesFrom || !exportLignesTo) return;
    setExportLignesPending(true);
    try {
      await exportLignesCsv(accessToken, exportLignesFrom, exportLignesTo);
      setExportLignesModal(false);
      setExportLignesFrom('');
      setExportLignesTo('');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur export lignes');
    } finally {
      setExportLignesPending(false);
    }
  }, [accessToken, exportLignesFrom, exportLignesTo]);

  const handleOpenPoste = useCallback(async () => {
    if (!accessToken) return;
    setError(null);
    setLoading(true);
    try {
      const openedAt = openedAtValue.trim()
        ? new Date(openedAtValue).toISOString()
        : undefined;
      const p = await openPoste(accessToken, openedAt ? { opened_at: openedAt } : undefined);
      setPoste(p);
      setOpenModal(false);
      setOpenedAtValue('');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur ouverture poste');
    } finally {
      setLoading(false);
    }
  }, [accessToken, openedAtValue]);

  const handleClosePoste = useCallback(async () => {
    if (!accessToken || !poste?.id) return;
    setError(null);
    setLoading(true);
    try {
      await closePoste(accessToken, poste.id);
      setPoste(null);
      setTickets([]);
      setTotalTickets(0);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur fermeture poste');
    } finally {
      setLoading(false);
    }
  }, [accessToken, poste?.id]);

  const handleCreateTicket = useCallback(async () => {
    if (!accessToken) return;
    setError(null);
    setLoading(true);
    try {
      const t = await createTicket(accessToken);
      if (poste?.id) {
        setTickets((prev) => [t, ...prev]);
        setTotalTickets((n) => n + 1);
      } else {
        setPoste({ id: t.poste_id } as PosteReceptionItem);
        setTickets([t]);
        setTotalTickets(1);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur création ticket');
    } finally {
      setLoading(false);
    }
  }, [accessToken, poste?.id]);

  return (
    <Stack gap="md" data-testid="reception-accueil-page">
      <Title order={1}>Réception</Title>
      {loading && <Text data-testid="reception-loading">Chargement…</Text>}
      {error && <Text c="red" data-testid="reception-error">{error}</Text>}

      <Group data-testid="reception-kpi-banner" align="flex-start" gap="lg">
        {statsLoading && <Text size="sm" c="dimmed">Chargement des indicateurs…</Text>}
        {!statsLoading && stats && (
          <>
            <Text size="sm"><strong>Tickets aujourd&apos;hui :</strong> {stats.tickets_today}</Text>
            <Text size="sm"><strong>Poids total (kg) :</strong> {stats.total_weight_kg}</Text>
            <Text size="sm"><strong>Lignes :</strong> {stats.lines_count}</Text>
          </>
        )}
      </Group>

      {!loading && !poste && !error && (
        <Text data-testid="reception-poste-status">Aucun poste ouvert</Text>
      )}
      {!loading && poste && (
        <Text data-testid="reception-poste-status">
          Poste ouvert le {new Date(poste.opened_at).toLocaleString()} (statut : {poste.status})
        </Text>
      )}

      <Group>
        {!poste ? (
          <Button
            data-testid="reception-open-poste-btn"
            onClick={() => setOpenModal(true)}
            loading={loading}
          >
            Ouvrir poste
          </Button>
        ) : (
          <>
            <Button
              data-testid="reception-create-ticket-btn"
              onClick={handleCreateTicket}
              loading={loading}
            >
              Créer ticket
            </Button>
            <Button
              variant="light"
              color="red"
              data-testid="reception-close-poste-btn"
              onClick={handleClosePoste}
              loading={loading}
            >
              Fermer poste
            </Button>
          </>
        )}
      </Group>

      <Button
        variant="light"
        data-testid="reception-export-lignes-btn"
        onClick={() => setExportLignesModal(true)}
      >
        Export lignes (période)
      </Button>

      <Modal
        opened={openModal}
        onClose={() => { setOpenModal(false); setOpenedAtValue(''); }}
        title="Ouverture de poste"
        data-testid="reception-open-poste-modal"
      >
        <Stack gap="sm">
          <Text size="sm" c="dimmed">
            Date d&apos;ouverture (optionnel, saisie différée) :
          </Text>
          <TextInput
            type="datetime-local"
            data-testid="reception-opened-at-input"
            value={openedAtValue}
            onChange={(e) => setOpenedAtValue(e.currentTarget.value)}
          />
          <Group justify="flex-end" mt="md">
            <Button variant="default" onClick={() => { setOpenModal(false); setOpenedAtValue(''); }}>
              Annuler
            </Button>
            <Button data-testid="reception-open-poste-submit" onClick={handleOpenPoste} loading={loading}>
              Confirmer
            </Button>
          </Group>
        </Stack>
      </Modal>

      <Modal
        opened={exportLignesModal}
        onClose={() => { setExportLignesModal(false); setExportLignesFrom(''); setExportLignesTo(''); }}
        title="Export lignes (période)"
        data-testid="reception-export-lignes-modal"
      >
        <Stack gap="sm">
          <TextInput
            type="date"
            label="Du"
            value={exportLignesFrom}
            onChange={(e) => setExportLignesFrom(e.currentTarget.value)}
            data-testid="reception-export-lignes-date-from"
          />
          <TextInput
            type="date"
            label="Au"
            value={exportLignesTo}
            onChange={(e) => setExportLignesTo(e.currentTarget.value)}
            data-testid="reception-export-lignes-date-to"
          />
          <Group justify="flex-end" mt="md">
            <Button variant="default" onClick={() => { setExportLignesModal(false); setExportLignesFrom(''); setExportLignesTo(''); }}>
              Annuler
            </Button>
            <Button
              data-testid="reception-export-lignes-submit"
              onClick={handleExportLignes}
              loading={exportLignesPending}
              disabled={!exportLignesFrom || !exportLignesTo}
            >
              Télécharger CSV
            </Button>
          </Group>
        </Stack>
      </Modal>

      {poste && (
        <Stack gap="xs" data-testid="reception-tickets-section">
          <Title order={2}>Tickets du poste ({totalTickets})</Title>
          <List listStyleType="none" data-testid="reception-tickets-list">
            {tickets.map((t) => (
              <List.Item key={t.id}>
                <Anchor
                  component={Link}
                  to={`/reception/tickets/${t.id}`}
                  data-testid={`reception-ticket-${t.id}`}
                >
                  Ticket {t.id.slice(0, 8)}… — {t.status} — {new Date(t.created_at).toLocaleString()}
                </Anchor>
              </List.Item>
            ))}
          </List>
        </Stack>
      )}
    </Stack>
  );
}
