import { useState } from 'react';
import { Button, Group, Modal, PasswordInput, Stack, Text } from '@mantine/core';

export type SharedWorkstationOverrideActivateModalProps = {
  readonly opened: boolean;
  readonly onClose: () => void;
  readonly onConfirm: (confirmationPin: string) => Promise<boolean>;
  readonly busy?: boolean;
  readonly error?: string | null;
};

export function SharedWorkstationOverrideActivateModal({
  opened,
  onClose,
  onConfirm,
  busy = false,
  error = null,
}: SharedWorkstationOverrideActivateModalProps) {
  const [pin, setPin] = useState('');

  const handleConfirm = async () => {
    const ok = await onConfirm(pin);
    if (ok) {
      setPin('');
    }
  };

  const handleClose = () => {
    setPin('');
    onClose();
  };

  return (
    <Modal
      opened={opened}
      onClose={handleClose}
      title="Activer override SuperAdmin"
      centered
      closeOnClickOutside={!busy}
      zIndex={450}
      data-testid="shared-workstation-override-modal"
    >
      <Stack gap="md">
        <Text size="sm">
          L&apos;override élargit vos permissions opérateur sur ce poste. L&apos;allowlist
          modules du poste et la configuration site restent applicables. Action auditée —
          confirmation par re-saisie de votre PIN opérateur.
        </Text>
        <PasswordInput
          label="PIN de confirmation"
          value={pin}
          onChange={(e) => setPin(e.currentTarget.value)}
          maxLength={4}
          data-testid="shared-workstation-override-pin"
        />
        {error ? (
          <Text size="sm" c="red" data-testid="shared-workstation-override-error">
            {error}
          </Text>
        ) : null}
        <Group justify="flex-end">
          <Button variant="default" onClick={handleClose} disabled={busy}>
            Annuler
          </Button>
          <Button
            color="orange"
            loading={busy}
            onClick={() => void handleConfirm()}
            data-testid="shared-workstation-override-confirm"
          >
            Activer
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}
