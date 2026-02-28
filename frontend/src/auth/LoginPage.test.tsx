/**
 * Tests LoginPage — Story 11.1. Smoke : rendu formulaire connexion.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AuthProvider } from './AuthContext';
import { LoginPage } from './LoginPage';

function renderLoginPage() {
  return render(
    <MantineProvider>
      <AuthProvider>
        <MemoryRouter>
          <LoginPage />
        </MemoryRouter>
      </AuthProvider>
    </MantineProvider>
  );
}

describe('LoginPage', () => {
  it('affiche le titre Connexion et le formulaire', () => {
    renderLoginPage();
    expect(screen.getByRole('heading', { name: /connexion/i })).toBeInTheDocument();
    expect(screen.getByTestId('login-form')).toBeInTheDocument();
  });
});
