/**
 * Tests accueil réception — Story 6.1, 11.3.
 * Vitest + React Testing Library + jsdom.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { ReceptionAccueilPage } from './ReceptionAccueilPage';
import * as receptionApi from '../api/reception';

vi.mock('../auth/AuthContext', () => ({
  useAuth: () => ({ accessToken: 'fake-token' }),
}));

function renderReceptionAccueil() {
  return render(
    <MantineProvider>
      <BrowserRouter>
        <ReceptionAccueilPage />
      </BrowserRouter>
    </MantineProvider>
  );
}

describe('ReceptionAccueilPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(receptionApi, 'getCurrentPoste');
    vi.spyOn(receptionApi, 'getTickets');
    vi.spyOn(receptionApi, 'getReceptionStatsLive');
    vi.spyOn(receptionApi, 'closeTicket');
  });

  it('affiche le titre Réception et le bouton Ouvrir poste quand aucun poste', async () => {
    (receptionApi.getCurrentPoste as ReturnType<typeof vi.fn>).mockResolvedValue(null);
    (receptionApi.getReceptionStatsLive as ReturnType<typeof vi.fn>).mockResolvedValue({
      tickets_today: 0,
      total_weight_kg: 0,
      lines_count: 0,
    });
    renderReceptionAccueil();
    expect(await screen.findByTestId('reception-accueil-page')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /réception/i })).toBeInTheDocument();
    expect(await screen.findByTestId('reception-open-poste-btn')).toBeInTheDocument();
  });

  it('affiche les KPI live après chargement de getReceptionStatsLive', async () => {
    (receptionApi.getCurrentPoste as ReturnType<typeof vi.fn>).mockResolvedValue(null);
    (receptionApi.getReceptionStatsLive as ReturnType<typeof vi.fn>).mockResolvedValue({
      tickets_today: 5,
      total_weight_kg: 120.5,
      lines_count: 42,
    });
    renderReceptionAccueil();
    const banner = await screen.findByTestId('reception-kpi-banner');
    expect(banner).toBeInTheDocument();
    expect(banner).toHaveTextContent('5');
    expect(banner).toHaveTextContent('120.5');
    expect(banner).toHaveTextContent('42');
    expect(receptionApi.getReceptionStatsLive).toHaveBeenCalledWith('fake-token');
  });

  it('affiche Créer ticket et Fermer poste quand un poste est ouvert', async () => {
    (receptionApi.getCurrentPoste as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 'poste-1',
      opened_by_user_id: 'user-1',
      opened_at: '2026-02-27T10:00:00Z',
      closed_at: null,
      status: 'opened',
      created_at: '2026-02-27T10:00:00Z',
      updated_at: '2026-02-27T10:00:00Z',
    });
    (receptionApi.getTickets as ReturnType<typeof vi.fn>).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
    });
    (receptionApi.getReceptionStatsLive as ReturnType<typeof vi.fn>).mockResolvedValue({
      tickets_today: 0,
      total_weight_kg: 0,
      lines_count: 0,
    });
    renderReceptionAccueil();
    expect(await screen.findByTestId('reception-create-ticket-btn')).toBeInTheDocument();
    expect(screen.getByTestId('reception-close-poste-btn')).toBeInTheDocument();
  });

  it('clic Fermer sur un ticket ouvert appelle closeTicket et retire le ticket de la liste', async () => {
    const ticketOpened = {
      id: 'ticket-1',
      poste_id: 'poste-1',
      benevole_user_id: 'user-1',
      created_at: '2026-02-27T12:00:00Z',
      closed_at: null,
      status: 'opened',
      updated_at: '2026-02-27T12:00:00Z',
    };
    (receptionApi.getCurrentPoste as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 'poste-1',
      opened_by_user_id: 'user-1',
      opened_at: '2026-02-27T10:00:00Z',
      closed_at: null,
      status: 'opened',
      created_at: '2026-02-27T10:00:00Z',
      updated_at: '2026-02-27T10:00:00Z',
    });
    (receptionApi.getTickets as ReturnType<typeof vi.fn>).mockResolvedValue({
      items: [ticketOpened],
      total: 1,
      page: 1,
      page_size: 20,
    });
    (receptionApi.getReceptionStatsLive as ReturnType<typeof vi.fn>).mockResolvedValue({
      tickets_today: 1,
      total_weight_kg: 0,
      lines_count: 0,
    });
    (receptionApi.closeTicket as ReturnType<typeof vi.fn>).mockResolvedValue({ ...ticketOpened, status: 'closed' });
    const user = userEvent.setup();
    renderReceptionAccueil();
    await screen.findByTestId('reception-tickets-section');
    const closeBtn = screen.getByTestId('reception-close-ticket-ticket-1');
    await user.click(closeBtn);
    await waitFor(() => {
      expect(receptionApi.closeTicket as ReturnType<typeof vi.fn>).toHaveBeenCalledWith('fake-token', 'ticket-1');
    });
  });
});
