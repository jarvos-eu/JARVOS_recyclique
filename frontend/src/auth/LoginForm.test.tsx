/**
 * Tests composant LoginForm — Story 3.1.
 * Vitest + React Testing Library + jsdom (convention projet).
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('affiche le formulaire avec champs identifiant et mot de passe', () => {
    render(<LoginForm />);
    expect(screen.getByTestId('login-form')).toBeInTheDocument();
    expect(screen.getByLabelText(/identifiant/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/mot de passe/i)).toBeInTheDocument();
    expect(screen.getByTestId('login-username')).toBeInTheDocument();
    expect(screen.getByTestId('login-password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /se connecter/i })).toBeInTheDocument();
  });

  it('affiche un message d erreur quand error est fourni', () => {
    render(<LoginForm error="Identifiants invalides" />);
    expect(screen.getByRole('alert')).toHaveTextContent('Identifiants invalides');
  });

  it('appelle onSubmit avec username et password a la soumission', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);
    await user.type(screen.getByTestId('login-username'), 'alice');
    await user.type(screen.getByTestId('login-password'), 'secret');
    await user.click(screen.getByTestId('login-submit'));
    expect(onSubmit).toHaveBeenCalledWith('alice', 'secret');
  });
});
