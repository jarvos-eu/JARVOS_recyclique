/**
 * Formulaire de connexion — Story 3.1.
 * Soumet username/password vers POST /v1/auth/login.
 */
import React, { useState } from 'react';

export interface LoginFormProps {
  onSubmit?: (username: string, password: string) => void;
  error?: string;
}

export function LoginForm({ onSubmit, error }: LoginFormProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit?.(username, password);
  };

  return (
    <form onSubmit={handleSubmit} data-testid="login-form" role="form" aria-label="Connexion">
      {error && <p role="alert">{error}</p>}
      <label htmlFor="login-username">Identifiant</label>
      <input
        id="login-username"
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
        autoComplete="username"
        data-testid="login-username"
      />
      <label htmlFor="login-password">Mot de passe</label>
      <input
        id="login-password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        autoComplete="current-password"
        data-testid="login-password"
      />
      <button type="submit" data-testid="login-submit">
        Se connecter
      </button>
    </form>
  );
}
