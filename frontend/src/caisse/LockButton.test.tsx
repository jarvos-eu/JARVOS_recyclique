/**
 * Tests LockButton — Story 3.3 (follow-up review).
 * Vitest + React Testing Library : affichage, appel lock au clic.
 */
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MantineProvider } from '@mantine/core';
import { AuthProvider } from '../auth/AuthContext';
import { CaisseProvider } from './CaisseContext';
import { LockButton } from './LockButton';

const mockLock = vi.fn();

vi.mock('./CaisseContext', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./CaisseContext')>();
  return {
    ...actual,
    useCaisse: () => ({
      isLocked: false,
      unlockedBy: null,
      unlockWithPin: vi.fn(),
      lock: mockLock,
    }),
  };
});

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

describe('LockButton', () => {
  beforeEach(() => {
    mockLock.mockClear();
  });

  it('affiche le bouton avec le libellé par défaut', () => {
    renderWithProviders(<LockButton />);
    const btn = screen.getByTestId('lock-button');
    expect(btn).toBeInTheDocument();
    expect(btn).toHaveTextContent('Reverrouiller');
  });

  it('affiche le contenu personnalisé quand fourni', () => {
    renderWithProviders(<LockButton>Verrouiller la caisse</LockButton>);
    expect(screen.getByTestId('lock-button')).toHaveTextContent('Verrouiller la caisse');
  });

  it('appelle lock au clic', async () => {
    const user = userEvent.setup();
    renderWithProviders(<LockButton />);
    await user.click(screen.getByTestId('lock-button'));
    expect(mockLock).toHaveBeenCalledTimes(1);
  });
});
