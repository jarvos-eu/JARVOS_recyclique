import { useCallback, useState } from 'react';
import { activateOverride, deactivateOverride } from '../../api/shared-workstation-override-client';
import { useSharedWorkstationEffectiveModules } from './SharedWorkstationEffectiveModulesProvider';
import { useSharedWorkstationOperatorSession } from './SharedWorkstationOperatorSessionProvider';
import { SharedWorkstationOverrideActivateControl } from './SharedWorkstationOverrideActivateControl';
import { SharedWorkstationOverrideActivateModal } from './SharedWorkstationOverrideActivateModal';
import { SharedWorkstationSuperAdminOverrideBanner } from './SharedWorkstationSuperAdminOverrideBanner';

export function SharedWorkstationOverrideShell() {
  const {
    operatorSessionActive,
    overrideActive,
    canActivateSuperAdminOverride,
    overrideSecondsRemaining,
    refreshSessionStatus,
  } = useSharedWorkstationOperatorSession();
  const { refreshEffectiveModules } = useSharedWorkstationEffectiveModules();
  const [modalOpen, setModalOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshAll = useCallback(async () => {
    await refreshSessionStatus();
    await refreshEffectiveModules();
  }, [refreshSessionStatus, refreshEffectiveModules]);

  const handleActivate = useCallback(
    async (confirmationPin: string): Promise<boolean> => {
      setBusy(true);
      setError(null);
      try {
        const result = await activateOverride(confirmationPin);
        if (!result.ok) {
          setError(result.message);
          return false;
        }
        await refreshAll();
        setModalOpen(false);
        return true;
      } finally {
        setBusy(false);
      }
    },
    [refreshAll],
  );

  const handleDeactivate = useCallback(async () => {
    setBusy(true);
    try {
      await deactivateOverride('user_exit');
      await refreshAll();
    } finally {
      setBusy(false);
    }
  }, [refreshAll]);

  if (!operatorSessionActive) {
    return null;
  }

  return (
    <>
      {overrideActive ? (
        <SharedWorkstationSuperAdminOverrideBanner
          overrideSecondsRemaining={overrideSecondsRemaining}
          onExit={() => void handleDeactivate()}
          busy={busy}
        />
      ) : null}
      {canActivateSuperAdminOverride ? (
        <SharedWorkstationOverrideActivateControl
          onOpen={() => {
            setError(null);
            setModalOpen(true);
          }}
          disabled={busy}
        />
      ) : null}
      <SharedWorkstationOverrideActivateModal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        onConfirm={handleActivate}
        busy={busy}
        error={error}
      />
    </>
  );
}
