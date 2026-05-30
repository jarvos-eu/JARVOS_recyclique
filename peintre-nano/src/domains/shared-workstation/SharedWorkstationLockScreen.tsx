import { useCallback, useState, type FormEvent } from 'react';
import { Button, PinInput, Stack, Text, TextInput, Title } from '@mantine/core';
import { verifySharedWorkstationOperatorPin } from '../../api/shared-workstation-operator-pin-client';
import { useSharedWorkstationOperatorSession } from './SharedWorkstationOperatorSessionProvider';

const NEUTRAL_ERROR = 'Identifiant ou PIN incorrect';
const LOCKOUT_ERROR = 'Trop de tentatives — réessayez dans quelques minutes';

export type SharedWorkstationLockScreenProps = {
  readonly deviceLabel?: string;
  readonly onUnlocked?: () => void;
};

export function SharedWorkstationLockScreen({
  deviceLabel,
  onUnlocked,
}: SharedWorkstationLockScreenProps) {
  const { refreshSessionStatus } = useSharedWorkstationOperatorSession();
  const [operatorId, setOperatorId] = useState('');
  const [pin, setPin] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [locked, setLocked] = useState(false);
  const [busy, setBusy] = useState(false);

  const onSubmit = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      if (locked || busy) return;
      setError(null);
      setBusy(true);
      try {
        const result = await verifySharedWorkstationOperatorPin({
          operator_user_id: operatorId.trim(),
          pin,
        });
        if (!result.ok) {
          if (result.code === 'SHARED_WORKSTATION_PIN_LOCKED' || result.status === 429) {
            setLocked(true);
            setError(LOCKOUT_ERROR);
          } else {
            setError(NEUTRAL_ERROR);
          }
          setPin('');
          return;
        }
        setPin('');
        const active = await refreshSessionStatus();
        if (active) {
          onUnlocked?.();
        }
      } finally {
        setBusy(false);
      }
    },
    [operatorId, pin, locked, busy, refreshSessionStatus, onUnlocked],
  );

  return (
    <div
      data-testid="shared-workstation-lock-screen"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 10000,
        background: 'var(--mantine-color-body)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
      }}
    >
      <form onSubmit={(e) => void onSubmit(e)} style={{ width: '100%', maxWidth: 420 }}>
        <Stack gap="md">
          <Title order={3}>Poste partagé verrouillé</Title>
          {deviceLabel ? (
            <Text size="sm" c="dimmed">
              {deviceLabel}
            </Text>
          ) : null}
          <Text size="sm">Saisissez votre identifiant opérateur et votre PIN à 4 chiffres.</Text>
          <TextInput
            data-testid="shared-workstation-operator-id"
            label="Identifiant opérateur (UUID)"
            value={operatorId}
            onChange={(ev) => setOperatorId(ev.currentTarget.value)}
            disabled={locked || busy}
            autoComplete="off"
          />
          <PinInput
            data-testid="shared-workstation-pin-input"
            length={4}
            type="number"
            mask
            value={pin}
            onChange={setPin}
            disabled={locked || busy}
            oneTimeCode
          />
          {error ? (
            <Text size="sm" c="red" role="alert">
              {error}
            </Text>
          ) : null}
          <Button
            type="submit"
            data-testid="shared-workstation-pin-submit"
            loading={busy}
            disabled={locked || operatorId.trim().length < 8 || pin.length !== 4}
          >
            Déverrouiller
          </Button>
        </Stack>
      </form>
    </div>
  );
}
