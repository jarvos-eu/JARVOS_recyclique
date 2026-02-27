/**
 * Tests AdminGuard — Story 8.1.
 * Vitest + RTL + MantineProvider.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminGuard } from './AdminGuard';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <MantineProvider>
      <MemoryRouter>{ui}</MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminGuard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders children when user has admin permission', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', username: 'admin' },
      permissions: ['admin'],
    });
    renderWithProviders(
      <AdminGuard>
        <span data-testid="child">Contenu protégé</span>
      </AdminGuard>
    );
    expect(screen.getByTestId('child')).toBeInTheDocument();
    expect(screen.getByText('Contenu protégé')).toBeInTheDocument();
  });

  it('shows forbidden message when user lacks admin permission', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', username: 'user' },
      permissions: ['operator'],
    });
    renderWithProviders(
      <AdminGuard>
        <span data-testid="child">Contenu</span>
      </AdminGuard>
    );
    expect(screen.getByTestId('admin-forbidden')).toBeInTheDocument();
    expect(screen.getByText(/Accès réservé aux administrateurs/)).toBeInTheDocument();
    expect(screen.queryByTestId('child')).not.toBeInTheDocument();
  });

  it('does not render children when user is null (redirect to login)', () => {
    mockUseAuth.mockReturnValue({ user: null, permissions: [] });
    renderWithProviders(
      <AdminGuard>
        <span data-testid="child">Contenu</span>
      </AdminGuard>
    );
    expect(screen.queryByTestId('child')).not.toBeInTheDocument();
    expect(screen.queryByTestId('admin-forbidden')).not.toBeInTheDocument();
  });
});
