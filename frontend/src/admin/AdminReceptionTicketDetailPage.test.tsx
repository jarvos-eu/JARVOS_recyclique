/**
 * Tests AdminReceptionTicketDetailPage — Story 8.4, 11.5.
 * Vitest + RTL + MantineProvider. Smoke : rendu, détail ticket, lignes.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminReceptionTicketDetailPage } from './AdminReceptionTicketDetailPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockGetTicket = vi.fn();
vi.mock('../api/reception', () => ({
  getTicket: (...args: unknown[]) => mockGetTicket(...args),
}));

function renderWithProviders(ticketId: string) {
  return render(
    <MantineProvider>
      <MemoryRouter initialEntries={[`/admin/reception-tickets/${ticketId}`]}>
        <Routes>
          <Route path="/admin/reception-tickets/:id" element={<AdminReceptionTicketDetailPage />} />
        </Routes>
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminReceptionTicketDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: { id: '1' },
      permissions: ['admin'],
      accessToken: 'token',
    });
    mockGetTicket.mockResolvedValue({
      id: 'ticket-123',
      poste_id: 'p1',
      benevole_user_id: null,
      created_at: '2026-01-01T12:00:00Z',
      closed_at: null,
      status: 'opened',
      updated_at: '2026-01-01T12:00:00Z',
      lignes: [
        {
          id: 'l1',
          ticket_id: 'ticket-123',
          poids_kg: 5,
          category_id: 'cat1',
          destination: 'Recyclage',
          notes: null,
          is_exit: false,
          created_at: '2026-01-01T12:00:00Z',
          updated_at: '2026-01-01T12:00:00Z',
        },
      ],
    });
  });

  it('affiche forbidden quand pas admin', () => {
    mockUseAuth.mockReturnValue({ permissions: [], accessToken: 'token' });
    renderWithProviders('ticket-123');
    expect(screen.getByTestId('admin-reception-ticket-forbidden')).toBeInTheDocument();
  });

  it('affiche le détail du ticket après chargement', async () => {
    renderWithProviders('ticket-123');
    await waitFor(() => {
      expect(mockGetTicket).toHaveBeenCalledWith('token', 'ticket-123');
    });
    await waitFor(() => {
      expect(screen.getByTestId('admin-reception-ticket-detail')).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /Ticket/ })).toBeInTheDocument();
      expect(screen.getByText(/Recyclage/)).toBeInTheDocument();
    });
  });
});
