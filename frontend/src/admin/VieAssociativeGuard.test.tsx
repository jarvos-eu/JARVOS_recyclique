/**
 * Tests VieAssociativeGuard — Story 8.7.
 * Vitest + RTL + MantineProvider.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { VieAssociativeGuard } from './VieAssociativeGuard';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <MantineProvider>
      <MemoryRouter>{ui}</MemoryRouter>
    </MantineProvider>
  );
}

describe('VieAssociativeGuard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders children when user has admin permission', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', username: 'admin' },
      permissions: ['admin'],
    });
    renderWithProviders(
      <VieAssociativeGuard>
        <span data-testid="child">Contenu vie asso</span>
      </VieAssociativeGuard>
    );
    expect(screen.getByTestId('child')).toBeInTheDocument();
  });

  it('renders children when user has vie_asso.access permission', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '2', username: 'benevole' },
      permissions: ['vie_asso.access'],
    });
    renderWithProviders(
      <VieAssociativeGuard>
        <span data-testid="child">Contenu vie asso</span>
      </VieAssociativeGuard>
    );
    expect(screen.getByTestId('child')).toBeInTheDocument();
  });

  it('shows forbidden when user has neither admin nor vie_asso.access', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '3', username: 'user' },
      permissions: ['reception.access'],
    });
    renderWithProviders(
      <VieAssociativeGuard>
        <span data-testid="child">Contenu</span>
      </VieAssociativeGuard>
    );
    expect(screen.getByTestId('vie-associative-forbidden')).toBeInTheDocument();
    expect(screen.getByText(/Accès réservé.*vie associative/)).toBeInTheDocument();
    expect(screen.queryByTestId('child')).not.toBeInTheDocument();
  });

  it('does not render children when user is null (redirect to login)', () => {
    mockUseAuth.mockReturnValue({ user: null, permissions: [] });
    renderWithProviders(
      <VieAssociativeGuard>
        <span data-testid="child">Contenu</span>
      </VieAssociativeGuard>
    );
    expect(screen.queryByTestId('child')).not.toBeInTheDocument();
    expect(screen.queryByTestId('vie-associative-forbidden')).not.toBeInTheDocument();
  });
});
