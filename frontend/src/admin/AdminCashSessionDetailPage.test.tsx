/**
 * Tests AdminCashSessionDetailPage — Story 8.2, 11.2 (Vitest + RTL + MantineProvider).
 * Smoke : rendu détail session, bouton rapport.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminCashSessionDetailPage } from './AdminCashSessionDetailPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

vi.mock('../api/caisse', () => ({
  getCashSession: vi.fn().mockResolvedValue({
    id: 'session-admin-1',
    operator_id: 'op-1',
    register_id: 'reg-1',
    site_id: 'site-1',
    initial_amount: 10000,
    current_amount: 15000,
    status: 'closed',
    opened_at: '2026-02-27T10:00:00Z',
    closed_at: '2026-02-27T18:00:00Z',
    current_step: 'exit',
    closing_amount: 15000,
    actual_amount: 14800,
    variance: -200,
    variance_comment: 'Manque 2 €',
    session_type: 'real',
    total_sales: 5000,
    total_items: 3,
    created_at: '2026-02-27T10:00:00Z',
    updated_at: '2026-02-27T18:00:00Z',
  }),
}));

vi.mock('../api/adminReports', () => ({
  getReportBySession: vi.fn().mockResolvedValue(new Blob(['report'])),
}));

function renderWithProviders(sessionId = 'session-admin-1') {
  return render(
    <MantineProvider>
      <MemoryRouter initialEntries={[`/admin/cash-sessions/${sessionId}`]}>
        <Routes>
          <Route path="/admin/cash-sessions/:id" element={<AdminCashSessionDetailPage />} />
        </Routes>
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminCashSessionDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      accessToken: 'token',
      permissions: ['admin'],
    });
  });

  it('affiche la page détail avec test id', async () => {
    renderWithProviders();
    expect(await screen.findByTestId('admin-session-detail-page')).toBeInTheDocument();
  });

  it('affiche les infos session (ouverture, fond, total ventes)', async () => {
    renderWithProviders();
    await screen.findByTestId('admin-session-detail-page');
    expect(screen.getByText(/Ouverture/)).toBeInTheDocument();
    expect(screen.getByText(/Fond de caisse/)).toBeInTheDocument();
    expect(screen.getByText(/Total ventes/)).toBeInTheDocument();
  });

  it('affiche le bouton télécharger rapport quand session fermée', async () => {
    renderWithProviders();
    expect(await screen.findByTestId('download-report')).toBeInTheDocument();
  });
});
