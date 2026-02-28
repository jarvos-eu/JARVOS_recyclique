/**
 * Tests AdminReceptionPage — Story 8.4, 11.5.
 * Vitest + RTL + MantineProvider. Smoke : rendu, onglets, stats, liste tickets.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminReceptionPage } from './AdminReceptionPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockGetReceptionStatsLive = vi.fn();
const mockGetTickets = vi.fn();
const mockPostExportBulk = vi.fn();
vi.mock('../api/reception', () => ({
  getReceptionStatsLive: (...args: unknown[]) => mockGetReceptionStatsLive(...args),
  getTickets: (...args: unknown[]) => mockGetTickets(...args),
}));
vi.mock('../api/adminHealthAudit', () => ({
  postAdminReceptionTicketsExportBulk: (...args: unknown[]) => mockPostExportBulk(...args),
}));

function renderWithProviders() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <AdminReceptionPage />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminReceptionPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: { id: '1', username: 'admin' },
      permissions: ['admin'],
      accessToken: 'token',
    });
    mockGetReceptionStatsLive.mockResolvedValue({
      tickets_today: 3,
      total_weight_kg: 42,
      lines_count: 10,
    });
    mockGetTickets.mockResolvedValue({
      items: [
        {
          id: 't1',
          poste_id: 'p1',
          benevole_user_id: null,
          created_at: '2026-01-01T12:00:00Z',
          closed_at: null,
          status: 'opened',
          updated_at: '2026-01-01T12:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
    });
  });

  it('affiche forbidden quand pas admin', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1' },
      permissions: [],
      accessToken: 'token',
    });
    renderWithProviders();
    expect(screen.getByTestId('admin-reception-forbidden')).toBeInTheDocument();
  });

  it('affiche la page avec onglets Stats et Tickets', async () => {
    renderWithProviders();
    await waitFor(() => {
      expect(mockGetReceptionStatsLive).toHaveBeenCalledWith('token');
      expect(mockGetTickets).toHaveBeenCalled();
    });
    expect(screen.getByTestId('admin-reception-page')).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Stats/ })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Tickets/ })).toBeInTheDocument();
  });

  it('affiche les stats quand API répond', async () => {
    renderWithProviders();
    await waitFor(() => {
      expect(screen.getByTestId('admin-reception-tickets-today')).toHaveTextContent('3');
      expect(screen.getByTestId('admin-reception-weight')).toHaveTextContent('42');
      expect(screen.getByTestId('admin-reception-lines')).toHaveTextContent('10');
    });
  });
});
