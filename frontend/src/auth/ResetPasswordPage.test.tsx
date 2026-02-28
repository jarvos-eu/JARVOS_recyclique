/**
 * Tests ResetPasswordPage — Story 11.1. Smoke : sans token affiche message lien invalide.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { ResetPasswordPage } from './ResetPasswordPage';

function renderResetPasswordPage(initialEntries: string[] = ['/reset-password']) {
  return render(
    <MantineProvider>
      <MemoryRouter initialEntries={initialEntries}>
        <ResetPasswordPage />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('ResetPasswordPage', () => {
  it('sans token affiche message lien invalide', () => {
    renderResetPasswordPage();
    expect(screen.getByRole('heading', { name: /réinitialisation du mot de passe/i })).toBeInTheDocument();
    expect(screen.getByText(/lien est invalide/i)).toBeInTheDocument();
  });
});
