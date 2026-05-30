import { Alert, Button, Paper, Stack, Text, TextInput, Title } from '@mantine/core';
import { useCallback, useEffect, useState, type FormEvent, type ReactNode } from 'react';
import { completeSharedWorkstationEnrollment } from '../../api/shared-workstation-enrollment-client';
import type { RegisteredWidgetProps } from '../../registry/widget-registry';
import {
  hadPriorDeviceEnrollment,
  hasDeviceIdentity,
  loadDeviceIdentity,
  saveDeviceIdentity,
} from './device-identity-store';

const ENROLLMENT_ERROR_LABELS: Record<string, string> = {
  ENROLLMENT_CODE_INVALID: 'Code invalide — vérifiez la saisie.',
  ENROLLMENT_CODE_EXPIRED: 'Code expiré — demandez un nouveau code au super-admin.',
  ENROLLMENT_CODE_CONSUMED: 'Code déjà utilisé.',
  DEVICE_ENROLLMENT_STATE_INVALID: 'État du poste incompatible — contactez le super-admin.',
};

/**
 * Enrôlement terrain poste partagé — route `/shared-workstation/enroll`.
 */
export function SharedWorkstationEnrollmentWidget(_: RegisteredWidgetProps): ReactNode {
  const [code, setCode] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{ deviceName: string } | null>(null);
  const [identityLost, setIdentityLost] = useState(false);

  useEffect(() => {
    void (async () => {
      const [has, hadPrior] = await Promise.all([
        hasDeviceIdentity(),
        hadPriorDeviceEnrollment(),
      ]);
      if (!has && hadPrior) setIdentityLost(true);
    })();
  }, []);

  const onSubmit = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      setError(null);
      setBusy(true);
      try {
        const trimmed = code.trim();
        if (!trimmed) {
          setError('Saisissez le code fourni par le super-admin.');
          return;
        }
        const res = await completeSharedWorkstationEnrollment({ code: trimmed });
        if (!res.ok) {
          const label = res.code ? ENROLLMENT_ERROR_LABELS[res.code] : undefined;
          setError(label ?? res.message);
          return;
        }
        try {
          await saveDeviceIdentity({
            device_id: res.device_id,
            device_secret: res.device_secret,
          });
        } catch {
          setError(
            "Enrôlement serveur réussi mais l'identité locale n'a pas pu être enregistrée — réessayez ou contactez le support.",
          );
          return;
        }
        setSuccess({ deviceName: res.device_name });
        setIdentityLost(false);
        if (typeof window !== 'undefined') {
          window.setTimeout(() => {
            window.history.replaceState({}, '', '/login');
          }, 2500);
        }
      } finally {
        setBusy(false);
      }
    },
    [code],
  );

  if (success) {
    return (
      <Stack gap="md" p="lg" maw={480} mx="auto" data-testid="shared-workstation-enrollment-success">
        <Title order={2}>Enrôlement réussi</Title>
        <Text>
          Poste <strong>{success.deviceName}</strong> enregistré. Identité enregistrée — connectez-vous.
        </Text>
      </Stack>
    );
  }

  return (
    <Stack gap="md" p="lg" maw={480} mx="auto" data-testid="shared-workstation-enrollment">
      <Title order={2}>Enrôlement du poste</Title>
      <Text size="sm" c="dimmed">
        Saisissez le code à usage unique fourni par le super-admin. Aucune connexion utilisateur requise à cette étape.
      </Text>
      {identityLost ? (
        <Alert color="orange" data-testid="shared-workstation-identity-lost-banner">
          Identité locale perdue sur ce navigateur — reconnectez ce poste avec un code « reconnecter ».
        </Alert>
      ) : null}
      <Paper component="form" onSubmit={(e) => void onSubmit(e)} p="md" withBorder>
        <Stack gap="sm">
          <TextInput
            label="Code d'enrôlement"
            value={code}
            onChange={(e) => setCode(e.currentTarget.value.toUpperCase())}
            data-testid="shared-workstation-enrollment-code"
            autoComplete="off"
            spellCheck={false}
          />
          {error ? (
            <Text size="sm" c="red" role="alert">
              {error}
            </Text>
          ) : null}
          <Button type="submit" loading={busy} data-testid="shared-workstation-enrollment-submit">
            Valider l'enrôlement
          </Button>
        </Stack>
      </Paper>
    </Stack>
  );
}

/** Utilitaire test — charge l'identité sans localStorage. */
export async function readStoredDeviceIdentityForTests() {
  return loadDeviceIdentity();
}
