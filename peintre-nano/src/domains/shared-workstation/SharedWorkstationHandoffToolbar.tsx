import { Button, Group } from '@mantine/core';
import type { OperatorSessionEndReason } from '../../api/shared-workstation-operator-session-client';

export type SharedWorkstationHandoffToolbarProps = {
  readonly onEndSession: (reason: OperatorSessionEndReason) => void;
  readonly busy?: boolean;
};

export function SharedWorkstationHandoffToolbar({
  onEndSession,
  busy = false,
}: SharedWorkstationHandoffToolbarProps) {
  return (
    <Group
      gap="xs"
      justify="flex-end"
      p="xs"
      style={{
        position: 'fixed',
        bottom: 0,
        right: 0,
        zIndex: 200,
        pointerEvents: 'auto',
      }}
      data-testid="shared-workstation-handoff-toolbar"
    >
      <Button
        variant="light"
        size="compact-sm"
        disabled={busy}
        onClick={() => onEndSession('handoff')}
        data-testid="shared-workstation-handoff"
      >
        Passer la main
      </Button>
      <Button
        variant="outline"
        color="red"
        size="compact-sm"
        disabled={busy}
        onClick={() => onEndSession('manual_lock')}
        data-testid="shared-workstation-lock-now-toolbar"
      >
        Verrouiller
      </Button>
    </Group>
  );
}
