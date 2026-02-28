/**
 * Tests CashRegisterPinPage — Story 11.1. Smoke : rendu clavier PIN.
 */
import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AuthProvider } from '../auth/AuthContext';
import { CaisseProvider } from './CaisseContext';
import { CashRegisterPinPage } from './CashRegisterPinPage';

function renderPinPage() {
  return render(
    <MantineProvider>
      <AuthProvider>
        <CaisseProvider>
          <MemoryRouter>
            <CashRegisterPinPage />
          </MemoryRouter>
        </CaisseProvider>
      </AuthProvider>
    </MantineProvider>
  );
}

describe('CashRegisterPinPage', () => {
  it('affiche la page et le clavier PIN', () => {
    renderPinPage();
    expect(screen.getByTestId('cash-register-pin-page')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /déverrouillage caisse/i })).toBeInTheDocument();
    expect(screen.getByTestId('pin-keypad')).toBeInTheDocument();
    expect(screen.getByTestId('pin-submit')).toBeInTheDocument();
  });
});
