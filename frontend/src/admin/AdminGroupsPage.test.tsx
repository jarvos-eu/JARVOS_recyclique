/**
 * Tests AdminGroupsPage — Story 11.6.
 * Vitest + RTL + MantineProvider. Pas d'import React inutile.
 */
import type { ReactElement } from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminGroupsPage } from './AdminGroupsPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockGetAdminGroups = vi.fn();
vi.mock('../api/adminGroups', () => ({
  getAdminGroups: (...args: unknown[]) => mockGetAdminGroups(...args),
  getAdminGroup: vi.fn(),
  createAdminGroup: vi.fn(),
  updateAdminGroup: vi.fn(),
  deleteAdminGroup: vi.fn(),
  addGroupPermissions: vi.fn(),
  removeGroupPermission: vi.fn(),
  addGroupUsers: vi.fn(),
  removeGroupUser: vi.fn(),
}));

function renderWithProviders(ui: ReactElement) {
  return render(
    <MantineProvider>
      <MemoryRouter>{ui}</MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminGroupsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      accessToken: 'token',
      permissions: ['admin'],
    });
    mockGetAdminGroups.mockResolvedValue([]);
  });

  it('affiche forbidden quand pas admin', () => {
    mockUseAuth.mockReturnValue({ accessToken: 'token', permissions: [] });
    renderWithProviders(<AdminGroupsPage />);
    expect(screen.getByTestId('admin-groups-forbidden')).toBeInTheDocument();
  });

  it('affiche la page avec titre et bouton Créer un groupe', async () => {
    renderWithProviders(<AdminGroupsPage />);
    await waitFor(() => {
      expect(screen.getByTestId('admin-groups-page')).toBeInTheDocument();
    });
    expect(screen.getByRole('heading', { name: /Groupes/ })).toBeInTheDocument();
    expect(screen.getByTestId('admin-groups-create')).toBeInTheDocument();
  });

  it('affiche le tableau des groupes après chargement', async () => {
    mockGetAdminGroups.mockResolvedValue([
      { id: 'g1', name: 'Groupe A', description: 'Desc A', created_at: '', updated_at: '' },
    ]);
    renderWithProviders(<AdminGroupsPage />);
    await waitFor(() => {
      expect(screen.getByTestId('group-row-g1')).toBeInTheDocument();
    });
    expect(screen.getByText('Groupe A')).toBeInTheDocument();
  });
});
