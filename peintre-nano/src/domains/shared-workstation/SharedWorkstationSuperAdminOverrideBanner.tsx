import { Alert, Button, Group, Text } from '@mantine/core';

export type SharedWorkstationSuperAdminOverrideBannerProps = {
  readonly overrideSecondsRemaining: number | null;
  readonly onExit: () => void;
  readonly busy?: boolean;
};

export function SharedWorkstationSuperAdminOverrideBanner({
  overrideSecondsRemaining,
  onExit,
  busy = false,
}: SharedWorkstationSuperAdminOverrideBannerProps) {
  const countdown =
    overrideSecondsRemaining != null && overrideSecondsRemaining >= 0
      ? overrideSecondsRemaining
      : null;

  return (
    <Alert
      color="orange"
      variant="filled"
      radius={0}
      data-testid="shared-workstation-override-banner"
      styles={{
        root: {
          position: 'sticky',
          top: 0,
          zIndex: 350,
          borderRadius: 0,
        },
      }}
    >
      <Group justify="space-between" wrap="nowrap">
        <Text size="sm" fw={600}>
          Mode override SuperAdmin actif
          {countdown != null ? (
            <>
              {' '}
              — expiration dans{' '}
              <span data-testid="shared-workstation-override-countdown">{countdown}</span>s
            </>
          ) : null}
        </Text>
        <Button
          size="compact-sm"
          variant="white"
          color="orange"
          disabled={busy}
          onClick={onExit}
          data-testid="shared-workstation-override-exit"
        >
          Quitter override
        </Button>
      </Group>
    </Alert>
  );
}
