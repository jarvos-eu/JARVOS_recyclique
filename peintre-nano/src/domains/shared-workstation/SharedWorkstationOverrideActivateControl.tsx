import { Button } from '@mantine/core';

export type SharedWorkstationOverrideActivateControlProps = {
  readonly onOpen: () => void;
  readonly disabled?: boolean;
};

export function SharedWorkstationOverrideActivateControl({
  onOpen,
  disabled = false,
}: SharedWorkstationOverrideActivateControlProps) {
  return (
    <Button
      variant="outline"
      color="orange"
      size="compact-sm"
      disabled={disabled}
      onClick={onOpen}
      data-testid="shared-workstation-override-activate"
      style={{
        position: 'fixed',
        top: 8,
        right: 8,
        zIndex: 300,
      }}
    >
      Override SuperAdmin
    </Button>
  );
}
