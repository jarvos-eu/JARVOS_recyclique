/**
 * Tests AdminPermissionsPage — Story 11.6.
 * Vitest + RTL + MantineProvider. Pas d'import React inutile.
 */
import type { ReactElement } from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminPermissionsPage } from './AdminPermissionsPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockGetAdminPermissions = vi.fn();
vi.mock('../api/adminPermissions', () => ({
  getAdminPermissions: (...args: unknown[]) => mockGetAdminPermissions(...args),
  getAdminPermission: vi.fn(),
  createAdminPermission: vi.fn(),
  updateAdminPermission: vi.fn(),
  deleteAdminPermission: vi.fn(),
}));

function renderWithProviders(ui: ReactElement) {
  return render(
    <MantineProvider>
      <MemoryRouter>{ui}</MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminPermissionsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      accessToken: 'token',
      permissions: ['admin'],
    });
    mockGetAdminPermissions.mockResolvedValue([]);
  });

  it('affiche forbidden quand pas admin', () => {
    mockUseAuth.mockReturnValue({ accessToken: 'token', permissions: [] });
    renderWithProviders(<AdminPermissionsPage />);
    expect(screen.getByTestId('admin-permissions-forbidden')).toBeInTheDocument();
  });

  it('affiche la page avec titre et bouton Créer une permission', async () => {
    renderWithProviders(<AdminPermissionsPage />);
    await waitFor(() => {
      expect(screen.getByTestId('admin-permissions-page')).toBeInTheDocument();
    });
    expect(screen.getByRole('heading', { name: /Permissions/ })).toBeInTheDocument();
    expect(screen.getByTestId('admin-permissions-create')).toBeInTheDocument();
  });

  it('affiche le tableau des permissions après chargement', async () => {
    mockGetAdminPermissions.mockResolvedValue([
      { id: 'p1', code: 'admin', label: 'Administrateur', created_at: '', updated_at: '' },
    ]);
    renderWithProviders(<AdminPermissionsPage />);
    await waitFor(() => {
      expect(screen.getByTestId('permission-row-p1')).toBeInTheDocument();
    });
    expect(screen.getByText('admin')).toBeInTheDocument();
  });
});
