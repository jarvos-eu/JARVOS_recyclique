import { Button, Group, Modal, Stack, Text } from '@mantine/core';

export type SharedWorkstationInactivityWarningModalProps = {
  readonly opened: boolean;
  readonly secondsUntilLock: number | null;
  readonly onContinue: () => void;
  readonly onLockNow: () => void;
};

export function SharedWorkstationInactivityWarningModal({
  opened,
  secondsUntilLock,
  onContinue,
  onLockNow,
}: SharedWorkstationInactivityWarningModalProps) {
  const countdown =
    secondsUntilLock != null && secondsUntilLock >= 0 ? secondsUntilLock : WARNING_DISPLAY_FALLBACK;

  return (
    <Modal
      opened={opened}
      onClose={onContinue}
      title="Inactivité détectée"
      centered
      closeOnClickOutside={false}
      closeOnEscape={false}
      data-testid="shared-workstation-inactivity-warning"
      zIndex={400}
    >
      <Stack gap="md">
        <Text size="sm">
          Votre session sera verrouillée dans{' '}
          <strong data-testid="shared-workstation-inactivity-countdown">{countdown}</strong>{' '}
          seconde{countdown !== 1 ? 's' : ''} par mesure de sécurité.
        </Text>
        <Group justify="flex-end">
          <Button
            variant="default"
            onClick={onContinue}
            data-testid="shared-workstation-inactivity-continue"
          >
            Continuer
          </Button>
          <Button
            color="red"
            onClick={onLockNow}
            data-testid="shared-workstation-lock-now"
          >
            Verrouiller maintenant
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}

const WARNING_DISPLAY_FALLBACK = 60;
