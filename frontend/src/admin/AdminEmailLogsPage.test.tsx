/**
 * Tests AdminEmailLogsPage — Story 8.4, 11.5.
 * Vitest + RTL + MantineProvider. Smoke : rendu, tableau logs.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminEmailLogsPage } from './AdminEmailLogsPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockGetAdminEmailLogs = vi.fn();
vi.mock('../api/adminHealthAudit', () => ({
  getAdminEmailLogs: (...args: unknown[]) => mockGetAdminEmailLogs(...args),
}));

function renderWithProviders() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <AdminEmailLogsPage />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminEmailLogsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: { id: '1' },
      permissions: ['admin'],
      accessToken: 'token',
    });
    mockGetAdminEmailLogs.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
    });
  });

  it('affiche forbidden quand pas admin', () => {
    mockUseAuth.mockReturnValue({ permissions: [], accessToken: 'token' });
    renderWithProviders();
    expect(screen.getByTestId('admin-email-logs-forbidden')).toBeInTheDocument();
  });

  it('affiche la page et le tableau après chargement', async () => {
    renderWithProviders();
    await waitFor(() => {
      expect(mockGetAdminEmailLogs).toHaveBeenCalledWith('token', expect.any(Object));
    });
    expect(screen.getByTestId('admin-email-logs-page')).toBeInTheDocument();
    expect(screen.getByTestId('admin-email-logs-table')).toBeInTheDocument();
    expect(screen.getByTestId('admin-email-logs-empty')).toBeInTheDocument();
  });
});
