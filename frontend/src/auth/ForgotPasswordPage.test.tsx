/**
 * Tests ForgotPasswordPage — Story 11.1. Smoke : rendu formulaire.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { ForgotPasswordPage } from './ForgotPasswordPage';

function renderForgotPasswordPage() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <ForgotPasswordPage />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('ForgotPasswordPage', () => {
  it('affiche le titre et le formulaire email', () => {
    renderForgotPasswordPage();
    expect(screen.getByRole('heading', { name: /mot de passe oublié/i })).toBeInTheDocument();
    expect(screen.getByTestId('forgot-password-form')).toBeInTheDocument();
  });
});
