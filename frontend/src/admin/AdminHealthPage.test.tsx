/**
 * Tests AdminHealthPage — Story 8.4.
 * Vitest + RTL + MantineProvider. Mock API et AuthContext.
 */
import type { ReactElement } from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminHealthPage } from './AdminHealthPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockGetAdminHealth = vi.fn();
const mockGetAdminHealthDatabase = vi.fn();
const mockGetAdminHealthScheduler = vi.fn();
vi.mock('../api/adminHealthAudit', () => ({
  getAdminHealth: (...args: unknown[]) => mockGetAdminHealth(...args),
  getAdminHealthDatabase: (...args: unknown[]) => mockGetAdminHealthDatabase(...args),
  getAdminHealthScheduler: (...args: unknown[]) => mockGetAdminHealthScheduler(...args),
}));

function renderWithProviders(ui: ReactElement) {
  return render(
    <MantineProvider>
      <MemoryRouter>{ui}</MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminHealthPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: { id: '1', username: 'admin' },
      permissions: ['admin'],
      accessToken: 'token',
    });
    mockGetAdminHealth.mockResolvedValue({
      status: 'ok',
      database: 'ok',
      redis: 'ok',
      push_worker: 'ok',
    });
    mockGetAdminHealthDatabase.mockResolvedValue({ status: 'ok' });
    mockGetAdminHealthScheduler.mockResolvedValue({
      status: 'ok',
      configured: true,
      running: true,
      last_error: null,
      last_success_at: null,
    });
  });

  it('affiche forbidden quand pas admin', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1' },
      permissions: [],
      accessToken: 'token',
    });
    renderWithProviders(<AdminHealthPage />);
    expect(screen.getByTestId('admin-health-forbidden')).toBeInTheDocument();
    expect(screen.getByText(/Accès réservé aux administrateurs/)).toBeInTheDocument();
  });

  it('appelle les APIs health et affiche le statut global', async () => {
    renderWithProviders(<AdminHealthPage />);
    await waitFor(() => {
      expect(mockGetAdminHealth).toHaveBeenCalledWith('token');
      expect(mockGetAdminHealthDatabase).toHaveBeenCalledWith('token');
      expect(mockGetAdminHealthScheduler).toHaveBeenCalledWith('token');
    });
    await waitFor(() => {
      expect(screen.getByTestId('admin-health-page')).toBeInTheDocument();
      expect(screen.getByTestId('health-status')).toHaveTextContent('ok');
      expect(screen.getByTestId('health-database')).toHaveTextContent('ok');
      expect(screen.getByTestId('health-redis')).toHaveTextContent('ok');
      expect(screen.getByTestId('health-scheduler')).toHaveTextContent('ok');
    });
  });

  it('affiche une alerte en cas d erreur API', async () => {
    mockGetAdminHealth.mockRejectedValue(new Error('Network error'));
    renderWithProviders(<AdminHealthPage />);
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });
});
