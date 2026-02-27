/**
 * Tests AppNav — visibilité entrée « Vie associative » (Story 8.7).
 * Vitest + RTL + MantineProvider.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AppNav } from './AppNav';

const mockUseAuth = vi.fn();
const mockUseCashRegisterLock = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));
vi.mock('./useCashRegisterLock', () => ({ useCashRegisterLock: () => mockUseCashRegisterLock() }));

function renderNav() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <AppNav />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('AppNav Vie associative (Story 8.7)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseCashRegisterLock.mockReturnValue({ isRestricted: false });
  });

  it('shows Vie associative link when user has admin', () => {
    mockUseAuth.mockReturnValue({ permissions: ['admin'] });
    renderNav();
    expect(screen.getByRole('link', { name: /Vie associative/ })).toBeInTheDocument();
  });

  it('shows Vie associative link when user has vie_asso.access', () => {
    mockUseAuth.mockReturnValue({ permissions: ['vie_asso.access'] });
    renderNav();
    expect(screen.getByRole('link', { name: /Vie associative/ })).toBeInTheDocument();
  });

  it('hides Vie associative link when user has neither admin nor vie_asso.access', () => {
    mockUseAuth.mockReturnValue({ permissions: ['reception.access'] });
    renderNav();
    expect(screen.queryByRole('link', { name: /Vie associative/ })).not.toBeInTheDocument();
  });

  it('hides Vie associative link when user has no permissions', () => {
    mockUseAuth.mockReturnValue({ permissions: [] });
    renderNav();
    expect(screen.queryByRole('link', { name: /Vie associative/ })).not.toBeInTheDocument();
  });
});
