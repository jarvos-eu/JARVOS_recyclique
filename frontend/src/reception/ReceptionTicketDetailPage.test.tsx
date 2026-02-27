/**
 * Tests détail ticket réception — Story 6.1, 6.2 (review follow-up).
 * Vitest + React Testing Library + jsdom.
 * Couvre : chargement, erreur, ajout ligne, modification, suppression, modal poids.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { ReceptionTicketDetailPage } from './ReceptionTicketDetailPage';
import * as receptionApi from '../api/reception';

vi.mock('../auth/AuthContext', () => ({
  useAuth: () => ({ accessToken: 'fake-token' }),
}));

beforeAll(() => {
  global.ResizeObserver = class ResizeObserver {
    observe = vi.fn();
    unobserve = vi.fn();
    disconnect = vi.fn();
  };
});

function renderDetail(ticketId: string) {
  return render(
    <MantineProvider>
      <MemoryRouter initialEntries={[`/reception/tickets/${ticketId}`]}>
        <Routes>
          <Route path="/reception/tickets/:ticketId" element={<ReceptionTicketDetailPage />} />
        </Routes>
      </MemoryRouter>
    </MantineProvider>
  );
}

const ticketWithLignes = (lignes: Array<{ id: string; poids_kg: number; destination: string; category_id?: string | null; notes?: string | null; is_exit?: boolean }>) => ({
  id: 'ticket-uuid-123',
  poste_id: 'poste-1',
  benevole_user_id: 'user-1',
  created_at: '2026-02-27T12:00:00Z',
  closed_at: null,
  status: 'opened',
  updated_at: '2026-02-27T12:00:00Z',
  lignes: lignes.map((l) => ({
    id: l.id,
    ticket_id: 'ticket-uuid-123',
    poids_kg: l.poids_kg,
    category_id: l.category_id ?? null,
    destination: l.destination,
    notes: l.notes ?? null,
    is_exit: l.is_exit ?? false,
    created_at: '2026-02-27T12:00:00Z',
    updated_at: '2026-02-27T12:00:00Z',
  })),
});

describe('ReceptionTicketDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(receptionApi, 'getTicket');
    vi.spyOn(receptionApi, 'getCategoriesEntryTickets').mockResolvedValue([]);
  });

  it('affiche le chargement puis le détail du ticket', async () => {
    (receptionApi.getTicket as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 'ticket-uuid-123',
      poste_id: 'poste-1',
      benevole_user_id: 'user-1',
      created_at: '2026-02-27T12:00:00Z',
      closed_at: null,
      status: 'opened',
      updated_at: '2026-02-27T12:00:00Z',
      lignes: [],
    });
    renderDetail('ticket-uuid-123');
    expect(screen.getByTestId('reception-ticket-detail-loading')).toBeInTheDocument();
    expect(await screen.findByTestId('reception-ticket-detail-page')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /ticket ticket-u/i })).toBeInTheDocument();
    expect(screen.getByText(/statut : opened/i)).toBeInTheDocument();
    expect(screen.getByTestId('reception-lignes-empty')).toBeInTheDocument();
  });

  it('affiche une erreur en cas d\'échec du chargement', async () => {
    (receptionApi.getTicket as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Ticket not found'));
    renderDetail('unknown-id');
    expect(await screen.findByTestId('reception-ticket-detail-error')).toBeInTheDocument();
    expect(screen.getByText(/ticket not found/i)).toBeInTheDocument();
  });

  it('affiche ID manquant quand pas de ticketId dans l\'URL', () => {
    render(
      <MantineProvider>
        <MemoryRouter initialEntries={['/reception/tickets/']}>
          <Routes>
            <Route path="/reception/tickets/:ticketId?" element={<ReceptionTicketDetailPage />} />
          </Routes>
        </MemoryRouter>
      </MantineProvider>
    );
    expect(screen.getByTestId('reception-ticket-detail-missing-id')).toBeInTheDocument();
  });

  it('ajoute une ligne : saisie et soumission appellent createLigne puis rechargent le ticket', async () => {
    const ticket = ticketWithLignes([]);
    (receptionApi.getTicket as ReturnType<typeof vi.fn>).mockResolvedValue(ticket);
    vi.spyOn(receptionApi, 'createLigne').mockResolvedValue({
      id: 'ligne-new-1',
      ticket_id: 'ticket-uuid-123',
      poids_kg: 10.5,
      category_id: null,
      destination: 'recyclage',
      notes: null,
      is_exit: false,
      created_at: '2026-02-27T12:00:00Z',
      updated_at: '2026-02-27T12:00:00Z',
    });
    const user = userEvent.setup();
    renderDetail('ticket-uuid-123');
    await screen.findByTestId('reception-ticket-detail-page');

    const poidsInput = screen.getByRole('textbox', { name: /poids \(kg\)/i });
    await user.clear(poidsInput);
    await user.type(poidsInput, '10.5');

    const destinationSelect = screen.getByTestId('reception-ligne-destination');
    await user.click(destinationSelect);
    const optionRecyclage = await screen.findByRole('option', { name: /recyclage/i });
    await user.click(optionRecyclage);

    const submitBtn = screen.getByTestId('reception-ligne-submit');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(receptionApi.createLigne).toHaveBeenCalledWith('fake-token', {
        ticket_id: 'ticket-uuid-123',
        poids_kg: 10.5,
        destination: 'recyclage',
        category_id: undefined,
        notes: undefined,
        is_exit: false,
      });
    });
    await waitFor(() => {
      expect(receptionApi.getTicket).toHaveBeenCalledTimes(2);
    });
  });

  it('modifie une ligne : ouvrir modal Modifier, changer poids, Enregistrer appelle updateLigne', async () => {
    const ticket = ticketWithLignes([{ id: 'ligne-1', poids_kg: 5, destination: 'revente' }]);
    (receptionApi.getTicket as ReturnType<typeof vi.fn>).mockResolvedValue(ticket);
    vi.spyOn(receptionApi, 'updateLigne').mockResolvedValue({
      ...ticket.lignes![0],
      poids_kg: 12,
    });
    const user = userEvent.setup();
    renderDetail('ticket-uuid-123');
    await screen.findByTestId('reception-ticket-detail-page');

    const editBtn = screen.getByTestId('reception-ligne-edit-ligne-1');
    await user.click(editBtn);

    expect(screen.getByTestId('reception-edit-ligne-modal')).toBeInTheDocument();
    const modal = within(screen.getByTestId('reception-edit-ligne-modal'));
    const modalPoidsInput = modal.getByRole('textbox', { name: /poids \(kg\)/i });
    await user.clear(modalPoidsInput);
    await user.type(modalPoidsInput, '12');

    const saveBtn = screen.getByRole('button', { name: /enregistrer/i });
    await user.click(saveBtn);

    await waitFor(() => {
      expect(receptionApi.updateLigne).toHaveBeenCalledWith('fake-token', 'ligne-1', expect.objectContaining({ poids_kg: 12 }));
    });
  });

  it('supprime une ligne : clic Supprimer + confirm appelle deleteLigne', async () => {
    const ticket = ticketWithLignes([{ id: 'ligne-1', poids_kg: 5, destination: 'revente' }]);
    (receptionApi.getTicket as ReturnType<typeof vi.fn>).mockResolvedValue(ticket);
    vi.spyOn(receptionApi, 'deleteLigne').mockResolvedValue();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
    const user = userEvent.setup();
    renderDetail('ticket-uuid-123');
    await screen.findByTestId('reception-ticket-detail-page');

    const deleteBtn = screen.getByTestId('reception-ligne-delete-ligne-1');
    await user.click(deleteBtn);

    await waitFor(() => {
      expect(confirmSpy).toHaveBeenCalledWith('Supprimer cette ligne ?');
      expect(receptionApi.deleteLigne).toHaveBeenCalledWith('fake-token', 'ligne-1');
    });
    confirmSpy.mockRestore();
  });

  it('modal poids : ouvrir, modifier poids, Enregistrer appelle updateLigneWeight', async () => {
    const ticket = ticketWithLignes([{ id: 'ligne-1', poids_kg: 5, destination: 'revente' }]);
    (receptionApi.getTicket as ReturnType<typeof vi.fn>).mockResolvedValue(ticket);
    vi.spyOn(receptionApi, 'updateLigneWeight').mockResolvedValue({
      ...ticket.lignes![0],
      poids_kg: 8,
    });
    const user = userEvent.setup();
    renderDetail('ticket-uuid-123');
    await screen.findByTestId('reception-ticket-detail-page');

    const weightBtn = screen.getByTestId('reception-ligne-weight-ligne-1');
    await user.click(weightBtn);

    expect(screen.getByTestId('reception-weight-ligne-modal')).toBeInTheDocument();
    const modalPoidsInput = screen.getByDisplayValue('5');
    await user.clear(modalPoidsInput);
    await user.type(modalPoidsInput, '8');

    const saveBtn = screen.getByRole('button', { name: /enregistrer/i });
    await user.click(saveBtn);

    await waitFor(() => {
      expect(receptionApi.updateLigneWeight).toHaveBeenCalledWith('fake-token', 'ticket-uuid-123', 'ligne-1', 8);
    });
  });

  it('bouton Export CSV appelle exportTicketCsv et déclenche le téléchargement', async () => {
    (receptionApi.getTicket as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 'ticket-uuid-123',
      poste_id: 'poste-1',
      benevole_user_id: 'user-1',
      created_at: '2026-02-27T12:00:00Z',
      closed_at: null,
      status: 'opened',
      updated_at: '2026-02-27T12:00:00Z',
      lignes: [],
    });
    vi.spyOn(receptionApi, 'createDownloadToken').mockResolvedValue({ token: 'fake-dl-token', expires_in_seconds: 300 });
    vi.spyOn(receptionApi, 'exportTicketCsv').mockResolvedValue();
    const user = userEvent.setup();
    renderDetail('ticket-uuid-123');
    await screen.findByTestId('reception-ticket-detail-page');

    const exportBtn = screen.getByTestId('reception-ticket-export-csv-btn');
    await user.click(exportBtn);

    await waitFor(() => {
      expect(receptionApi.exportTicketCsv).toHaveBeenCalledWith('fake-token', 'ticket-uuid-123');
    });
  });
});
