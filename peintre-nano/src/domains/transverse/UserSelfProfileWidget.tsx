import { Alert, Button, Paper, PasswordInput, Stack, Text, Title } from '@mantine/core';
import { useCallback, useEffect, useState, type ReactNode } from 'react';
import {
  fetchUsersMeProfile,
  putUsersMePin,
  type UsersMeProfileDto,
} from '../../api/users-me-client';
import { useAuthPort } from '../../app/auth/AuthRuntimeProvider';
import type { RegisteredWidgetProps } from '../../registry/widget-registry';

const PIN_PATTERN = /^\d{4}$/;

function displayName(profile: UsersMeProfileDto | null): string {
  if (!profile) return '—';
  const parts = [profile.first_name, profile.last_name].filter((p) => p?.trim());
  if (parts.length) return parts.join(' ');
  return profile.username?.trim() || profile.email?.trim() || profile.id;
}

/**
 * Story 28.2 — Mon profil self-service : coordonnées lecture seule + gestion PIN (`PUT /v1/users/me/pin`).
 */
export function UserSelfProfileWidget(_props: RegisteredWidgetProps): ReactNode {
  const auth = useAuthPort();
  const [profile, setProfile] = useState<UsersMeProfileDto | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [pin, setPin] = useState('');
  const [pinConfirm, setPinConfirm] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [pinBusy, setPinBusy] = useState(false);
  const [pinFeedback, setPinFeedback] = useState<{ kind: 'ok' | 'error'; text: string } | null>(null);

  const reloadProfile = useCallback(async () => {
    setLoadError(null);
    const me = await fetchUsersMeProfile(auth);
    if (!me) {
      setLoadError('Impossible de charger votre profil.');
      setProfile(null);
      return;
    }
    setProfile(me);
  }, [auth]);

  useEffect(() => {
    void reloadProfile();
  }, [reloadProfile]);

  const onSubmitPin = async () => {
    setPinFeedback(null);
    if (!PIN_PATTERN.test(pin)) {
      setPinFeedback({ kind: 'error', text: 'Le code PIN doit comporter exactement 4 chiffres.' });
      return;
    }
    if (pin !== pinConfirm) {
      setPinFeedback({ kind: 'error', text: 'Les deux saisies du PIN ne correspondent pas.' });
      return;
    }
    setPinBusy(true);
    const payload =
      currentPassword.trim().length > 0
        ? { pin, current_password: currentPassword }
        : { pin };
    const res = await putUsersMePin(auth, payload);
    setPinBusy(false);
    if (!res.ok) {
      setPinFeedback({ kind: 'error', text: res.detail });
      return;
    }
    setPin('');
    setPinConfirm('');
    setCurrentPassword('');
    setPinFeedback({ kind: 'ok', text: 'Votre code PIN a été enregistré.' });
  };

  return (
    <Stack gap="md" data-testid="widget-user-self-profile">
      <Title order={2}>Mon profil</Title>

      {loadError ? (
        <Alert color="red" title="Profil indisponible" data-testid="user-profile-load-error">
          {loadError}
        </Alert>
      ) : null}

      <Paper withBorder p="md" data-testid="user-profile-readonly">
        <Stack gap="xs">
          <Text fw={600}>{displayName(profile)}</Text>
          <Text size="sm" c="dimmed">
            Identifiant : {profile?.username ?? '—'}
          </Text>
          <Text size="sm">E-mail : {profile?.email ?? '—'}</Text>
          <Text size="sm">Téléphone : {profile?.phone_number ?? '—'}</Text>
          <Text size="sm">Adresse : {profile?.address ?? '—'}</Text>
        </Stack>
      </Paper>

      <Paper withBorder p="md" data-testid="user-profile-pin-section">
        <Stack gap="sm">
          <Title order={4}>Code PIN opérateur</Title>
          <Text size="sm" c="dimmed">
            Le PIN comporte 4 chiffres. Il est requis pour certaines actions sur poste partagé ou caisse.
            Le mot de passe du compte n&apos;est demandé que si vous modifiez un PIN déjà défini.
          </Text>
          {pinFeedback ? (
            <Alert
              color={pinFeedback.kind === 'ok' ? 'green' : 'red'}
              data-testid={pinFeedback.kind === 'ok' ? 'user-profile-pin-success' : 'user-profile-pin-error'}
            >
              {pinFeedback.text}
            </Alert>
          ) : null}
          <PasswordInput
            label="Nouveau PIN"
            value={pin}
            onChange={(e) => setPin(e.currentTarget.value.replace(/\D/g, '').slice(0, 4))}
            inputMode="numeric"
            autoComplete="off"
            data-testid="user-profile-pin-input"
          />
          <PasswordInput
            label="Confirmer le PIN"
            value={pinConfirm}
            onChange={(e) => setPinConfirm(e.currentTarget.value.replace(/\D/g, '').slice(0, 4))}
            inputMode="numeric"
            autoComplete="off"
            data-testid="user-profile-pin-confirm-input"
          />
          <PasswordInput
            label="Mot de passe du compte"
            description="Requis uniquement pour remplacer un PIN déjà défini."
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.currentTarget.value)}
            autoComplete="current-password"
            data-testid="user-profile-current-password-input"
          />
          <Button
            onClick={() => void onSubmitPin()}
            loading={pinBusy}
            data-testid="user-profile-pin-submit"
          >
            Enregistrer le PIN
          </Button>
        </Stack>
      </Paper>
    </Stack>
  );
}
