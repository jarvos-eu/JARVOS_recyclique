/**
 * Page Connexion par PIN (caisse) — Story 11.1.
 * Route /cash-register/pin : clavier 4–6 chiffres, POST /v1/auth/pin, redirection vers dashboard caisse.
 * Aligné sur le rendu 1.4.4 (même logique que PinUnlockModal en page pleine).
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Title, Button, Stack, SimpleGrid, Alert, TextInput, Paper } from '@mantine/core';
import { useCaisse } from './CaisseContext';

const DIGITS = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '0'];

export function CashRegisterPinPage() {
  const { unlockWithPin } = useCaisse();
  const navigate = useNavigate();
  const [pin, setPin] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleDigit = (d: string) => {
    if (pin.length < 6) {
      setPin((p) => p + d);
      setError(null);
    }
  };

  const handleBackspace = () => {
    setPin((p) => p.slice(0, -1));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pin.length < 4 || pin.length > 6) {
      setError('Saisissez 4 à 6 chiffres');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await unlockWithPin(pin);
      navigate('/caisse', { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'PIN incorrect');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack gap="lg" maw={320} mx="auto" mt="xl" p="md" data-testid="cash-register-pin-page">
      <Title order={1}>Déverrouillage caisse</Title>
      <Paper p="lg" shadow="sm" radius="md" withBorder>
        <form onSubmit={handleSubmit} data-testid="pin-unlock-form">
          <Stack gap="md">
            {error && (
              <Alert role="alert" color="red" title="Erreur" data-testid="pin-error">
                {error}
              </Alert>
            )}
            <TextInput
              id="pin-display"
              label="Code PIN"
              type="password"
              readOnly
              value={pin.replace(/./g, '•')}
              aria-label="PIN masqué"
              data-testid="pin-display"
              autoComplete="off"
            />
            <SimpleGrid cols={3} spacing="xs" data-testid="pin-keypad">
              {DIGITS.map((d) => (
                <Button
                  key={d}
                  type="button"
                  variant="default"
                  onClick={() => handleDigit(d)}
                  disabled={loading}
                  data-testid={`pin-key-${d}`}
                >
                  {d}
                </Button>
              ))}
              <Button
                type="button"
                variant="light"
                onClick={handleBackspace}
                disabled={loading || pin.length === 0}
                data-testid="pin-backspace"
              >
                ←
              </Button>
            </SimpleGrid>
            <Button
              type="submit"
              disabled={loading || pin.length < 4}
              data-testid="pin-submit"
              loading={loading}
            >
              {loading ? 'Vérification…' : 'Valider'}
            </Button>
          </Stack>
        </form>
      </Paper>
    </Stack>
  );
}
