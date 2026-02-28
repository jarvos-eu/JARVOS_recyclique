/**
 * Tests AdminSessionManagerPage — Story 8.2, 11.4.
 * Vitest + RTL + MantineProvider. Smoke : rendu, filtres, liste.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminSessionManagerPage } from './AdminSessionManagerPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockGetSites = vi.fn();
const mockGetCashRegisters = vi.fn();
const mockGetUsers = vi.fn();
const mockGetCashSessionsList = vi.fn();
vi.mock('../api/admin', () => ({
  getSites: (...args: unknown[]) => mockGetSites(...args),
  getCashRegisters: (...args: unknown[]) => mockGetCashRegisters(...args),
  getUsers: (...args: unknown[]) => mockGetUsers(...args),
}));
vi.mock('../api/caisse', () => ({
  getCashSessionsList: (...args: unknown[]) => mockGetCashSessionsList(...args),
}));

function renderWithProviders() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <AdminSessionManagerPage />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminSessionManagerPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({ accessToken: 'token', permissions: ['admin'] });
    mockGetSites.mockResolvedValue([]);
    mockGetCashRegisters.mockResolvedValue([]);
    mockGetUsers.mockResolvedValue([]);
    mockGetCashSessionsList.mockResolvedValue([]);
  });

  it('renders page with title and filters', async () => {
    renderWithProviders();
    await screen.findByTestId('admin-sessions-loading');
    expect(screen.getByTestId('admin-session-manager-page')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Gestionnaire de sessions caisse/ })).toBeInTheDocument();
    expect(screen.getByTestId('filter-date-from')).toBeInTheDocument();
    expect(screen.getByTestId('filter-status')).toBeInTheDocument();
  });

  it('shows forbidden when user lacks admin permission', () => {
    mockUseAuth.mockReturnValue({ accessToken: null, permissions: ['operator'] });
    renderWithProviders();
    expect(screen.getByTestId('admin-session-manager-forbidden')).toBeInTheDocument();
  });

  it('shows empty state when no sessions', async () => {
    renderWithProviders();
    await screen.findByTestId('admin-sessions-empty');
    expect(screen.getByTestId('admin-sessions-table')).toBeInTheDocument();
  });
});
