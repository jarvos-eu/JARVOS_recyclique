/**
 * Tests AdminQuickAnalysisPage — Story 11.6.
 * Vitest + RTL + MantineProvider. Pas d'import React inutile.
 */
import type { ReactElement } from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminQuickAnalysisPage } from './AdminQuickAnalysisPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockGetDashboardStats = vi.fn();
vi.mock('../api/adminDashboard', () => ({
  getDashboardStats: (...args: unknown[]) => mockGetDashboardStats(...args),
}));

function renderWithProviders(ui: ReactElement) {
  return render(
    <MantineProvider>
      <MemoryRouter>{ui}</MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminQuickAnalysisPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      accessToken: 'token',
      permissions: ['admin'],
    });
    mockGetDashboardStats.mockResolvedValue({ users_count: 5, sites_count: 2 });
  });

  it('affiche forbidden quand pas admin', () => {
    mockUseAuth.mockReturnValue({ accessToken: 'token', permissions: [] });
    renderWithProviders(<AdminQuickAnalysisPage />);
    expect(screen.getByTestId('admin-quick-analysis-forbidden')).toBeInTheDocument();
  });

  it('affiche la page avec titre Analyse rapide', async () => {
    renderWithProviders(<AdminQuickAnalysisPage />);
    await waitFor(() => {
      expect(screen.getByTestId('admin-quick-analysis-page')).toBeInTheDocument();
    });
    expect(screen.getByRole('heading', { name: /Analyse rapide/ })).toBeInTheDocument();
  });

  it('affiche les indicateurs quand stats disponibles', async () => {
    renderWithProviders(<AdminQuickAnalysisPage />);
    await waitFor(() => {
      expect(screen.getByTestId('quick-stat-users')).toBeInTheDocument();
    });
    expect(screen.getByText('5')).toBeInTheDocument();
  });
});
