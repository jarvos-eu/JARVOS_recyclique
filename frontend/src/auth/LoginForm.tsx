/**
 * Formulaire de connexion — Story 3.1, 11.1.
 * Soumet username/password vers POST /v1/auth/login. Rendu Mantine aligné 1.4.4.
 */
import React, { useState } from 'react';
import { TextInput, PasswordInput, Button, Stack, Alert, Paper } from '@mantine/core';

export interface LoginFormProps {
  onSubmit?: (username: string, password: string) => void;
  error?: string;
  loading?: boolean;
}

export function LoginForm({ onSubmit, error, loading }: LoginFormProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit?.(username, password);
  };

  return (
    <Paper p="lg" shadow="sm" radius="md" withBorder>
      <form onSubmit={handleSubmit} data-testid="login-form" role="form" aria-label="Connexion">
        <Stack gap="md">
          {error && (
            <Alert role="alert" color="red" title="Erreur" data-testid="login-error">
              {error}
            </Alert>
          )}
          <TextInput
            id="login-username"
            label="Identifiant"
            placeholder="Nom d'utilisateur"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
            data-testid="login-username"
          />
          <PasswordInput
            id="login-password"
            label="Mot de passe"
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            data-testid="login-password"
          />
          <Button type="submit" data-testid="login-submit" loading={loading}>
            Se connecter
          </Button>
        </Stack>
      </form>
    </Paper>
  );
}
