/**
 * Tests composant LoginForm — Story 3.1, 11.1.
 * Vitest + React Testing Library + jsdom (convention projet). Mantine : wrapper MantineProvider.
 */
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MantineProvider } from '@mantine/core';
import { LoginForm } from './LoginForm';

function renderWithMantine(ui: React.ReactElement) {
  return render(<MantineProvider>{ui}</MantineProvider>);
}

describe('LoginForm', () => {
  it('affiche le formulaire avec champs identifiant et mot de passe', () => {
    renderWithMantine(<LoginForm />);
    expect(screen.getByTestId('login-form')).toBeInTheDocument();
    expect(screen.getByLabelText(/identifiant/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/mot de passe/i)).toBeInTheDocument();
    expect(screen.getByTestId('login-username')).toBeInTheDocument();
    expect(screen.getByTestId('login-password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /se connecter/i })).toBeInTheDocument();
  });

  it('affiche un message d erreur quand error est fourni', () => {
    renderWithMantine(<LoginForm error="Identifiants invalides" />);
    expect(screen.getByRole('alert')).toHaveTextContent('Identifiants invalides');
  });

  it('appelle onSubmit avec username et password a la soumission', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderWithMantine(<LoginForm onSubmit={onSubmit} />);
    await user.type(screen.getByTestId('login-username'), 'alice');
    await user.type(screen.getByTestId('login-password'), 'secret');
    await user.click(screen.getByTestId('login-submit'));
    expect(onSubmit).toHaveBeenCalledWith('alice', 'secret');
  });
});
