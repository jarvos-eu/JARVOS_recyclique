/**
 * Tests AdminDashboardPage — Story 8.1, 11.4.
 * Vitest + RTL + MantineProvider. Smoke : rendu, liens, stats optionnels.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminDashboardPage } from './AdminDashboardPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockGetPaheko = vi.fn();
const mockGetDashboardStats = vi.fn();
vi.mock('../api/adminPahekoCompta', () => ({ getPahekoComptaUrl: (...args: unknown[]) => mockGetPaheko(...args) }));
vi.mock('../api/adminDashboard', () => ({ getDashboardStats: (...args: unknown[]) => mockGetDashboardStats(...args) }));

function renderWithProviders() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <AdminDashboardPage />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminDashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({ accessToken: 'token', permissions: ['admin'] });
    mockGetPaheko.mockResolvedValue({ url: null });
    mockGetDashboardStats.mockResolvedValue(null);
  });

  it('renders page with Admin title', () => {
    renderWithProviders();
    expect(screen.getByTestId('page-admin')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Admin/ })).toBeInTheDocument();
  });

  it('shows navigation links when admin', async () => {
    renderWithProviders();
    expect(screen.getByRole('link', { name: /Utilisateurs/ })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Sites/ })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Rapports caisse/ })).toBeInTheDocument();
  });

  it('shows stats cards when API returns stats', async () => {
    mockGetDashboardStats.mockResolvedValue({
      users_count: 5,
      sites_count: 2,
      cash_registers_count: 3,
    });
    renderWithProviders();
    await screen.findByTestId('dashboard-stat-users');
    expect(screen.getByTestId('dashboard-stat-users')).toHaveTextContent('5');
    expect(screen.getByTestId('dashboard-stat-sites')).toHaveTextContent('2');
    expect(screen.getByTestId('dashboard-stat-registers')).toHaveTextContent('3');
  });

  it('does not show stats when getDashboardStats returns null', () => {
    mockGetDashboardStats.mockResolvedValue(null);
    renderWithProviders();
    expect(screen.queryByTestId('dashboard-stat-users')).not.toBeInTheDocument();
  });
});
