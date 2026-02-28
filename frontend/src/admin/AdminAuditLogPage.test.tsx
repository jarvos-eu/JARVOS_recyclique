/**
 * Tests AdminAuditLogPage — Story 8.4, 11.5.
 * Vitest + RTL + MantineProvider. Smoke : rendu, filtres, tableau.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminAuditLogPage } from './AdminAuditLogPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockGetAdminAuditLog = vi.fn();
vi.mock('../api/adminHealthAudit', () => ({
  getAdminAuditLog: (...args: unknown[]) => mockGetAdminAuditLog(...args),
}));

function renderWithProviders() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <AdminAuditLogPage />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminAuditLogPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: { id: '1' },
      permissions: ['admin'],
      accessToken: 'token',
    });
    mockGetAdminAuditLog.mockResolvedValue({
      items: [
        {
          id: 'e1',
          timestamp: '2026-01-01T12:00:00Z',
          user_id: 'u1',
          action: 'login',
          resource_type: 'user',
          resource_id: 'u1',
          details: 'OK',
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
    });
  });

  it('affiche forbidden quand pas admin', () => {
    mockUseAuth.mockReturnValue({ permissions: [], accessToken: 'token' });
    renderWithProviders();
    expect(screen.getByTestId('admin-audit-log-forbidden')).toBeInTheDocument();
  });

  it('affiche la page et le tableau après chargement', async () => {
    renderWithProviders();
    await waitFor(() => {
      expect(mockGetAdminAuditLog).toHaveBeenCalledWith('token', expect.any(Object));
    });
    expect(screen.getByTestId('admin-audit-log-page')).toBeInTheDocument();
    expect(screen.getByTestId('admin-audit-log-table')).toBeInTheDocument();
    expect(screen.getByTestId('filter-date-from')).toBeInTheDocument();
    expect(screen.getByTestId('filter-date-to')).toBeInTheDocument();
  });
});
