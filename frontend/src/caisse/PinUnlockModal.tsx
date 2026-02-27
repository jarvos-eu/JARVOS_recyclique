/**
 * Modal déverrouillage par PIN — Story 3.3.
 * Clavier 4–6 chiffres, champ masqué, appel POST /v1/auth/pin.
 * Convention projet : Mantine (Modal, Button, TextInput).
 */
import React, { useState } from 'react';
import { Modal, Button, TextInput, Stack, SimpleGrid, Alert } from '@mantine/core';
import { useCaisse } from './CaisseContext';

export interface PinUnlockModalProps {
  onClose?: () => void;
  /** Longueur PIN attendue (4–6). */
  pinLength?: number;
}

const DIGITS = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '0'];

export function PinUnlockModal({ onClose, pinLength = 4 }: PinUnlockModalProps) {
  const { unlockWithPin } = useCaisse();
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
      onClose?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'PIN incorrect');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      opened
      onClose={onClose ?? (() => {})}
      title="Déverrouiller la caisse"
      aria-label="Déverrouillage par PIN"
      data-testid="pin-unlock-modal"
    >
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
            disabled={loading || pin.length < pinLength}
            data-testid="pin-submit"
            loading={loading}
          >
            {loading ? 'Vérification…' : 'Valider'}
          </Button>
        </Stack>
      </form>
    </Modal>
  );
}
