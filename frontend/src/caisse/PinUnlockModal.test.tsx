/**
 * Tests PinUnlockModal — Story 3.3.
 * Vitest + React Testing Library + jsdom (convention projet).
 */
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MantineProvider } from '@mantine/core';
import { AuthProvider } from '../auth/AuthContext';
import { CaisseProvider } from './CaisseContext';
import { PinUnlockModal } from './PinUnlockModal';

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <MantineProvider>
      <AuthProvider>
        <CaisseProvider>
          {ui}
        </CaisseProvider>
      </AuthProvider>
    </MantineProvider>
  );
}

describe('PinUnlockModal', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('affiche le modal avec titre et clavier PIN', () => {
    renderWithProviders(<PinUnlockModal />);
    expect(screen.getByRole('dialog', { name: /déverrouiller la caisse/i })).toBeInTheDocument();
    expect(screen.getByText(/déverrouiller la caisse/i)).toBeInTheDocument();
    expect(screen.getByTestId('pin-unlock-form')).toBeInTheDocument();
    expect(screen.getByTestId('pin-display')).toBeInTheDocument();
    expect(screen.getByTestId('pin-key-1')).toBeInTheDocument();
    expect(screen.getByTestId('pin-submit')).toBeInTheDocument();
  });

  it('affiche un message d erreur en cas d echec API', async () => {
    const user = userEvent.setup();
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Invalid PIN' }),
    } as Response);
    renderWithProviders(<PinUnlockModal />);
    await user.click(screen.getByTestId('pin-key-1'));
    await user.click(screen.getByTestId('pin-key-2'));
    await user.click(screen.getByTestId('pin-key-3'));
    await user.click(screen.getByTestId('pin-key-4'));
    await user.click(screen.getByTestId('pin-submit'));
    expect(await screen.findByRole('alert')).toHaveTextContent(/invalid pin|erreur/i);
  });

  it('deverrouille et met a jour l etat en cas de succes', async () => {
    const user = userEvent.setup();
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_token: 'at',
        refresh_token: 'rt',
        token_type: 'bearer',
        user: { id: 'u1', username: 'op', email: 'op@test', role: 'operator', status: 'active', first_name: 'Op', last_name: 'Test' },
      }),
    } as Response);
    const onClose = vi.fn();
    renderWithProviders(<PinUnlockModal onClose={onClose} />);
    await user.click(screen.getByTestId('pin-key-1'));
    await user.click(screen.getByTestId('pin-key-2'));
    await user.click(screen.getByTestId('pin-key-3'));
    await user.click(screen.getByTestId('pin-key-4'));
    await user.click(screen.getByTestId('pin-submit'));
    await vi.waitFor(() => {
      expect(onClose).toHaveBeenCalled();
    });
  });
});
