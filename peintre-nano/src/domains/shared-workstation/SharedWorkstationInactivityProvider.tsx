import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import {
  fetchOperatorSessionStatus,
  type OperatorSessionEndReason,
} from '../../api/shared-workstation-operator-session-client';
import {
  useSharedWorkstationLockRequired,
  useSharedWorkstationOperatorSession,
} from './SharedWorkstationOperatorSessionProvider';
import { SharedWorkstationHandoffToolbar } from './SharedWorkstationHandoffToolbar';
import { SharedWorkstationInactivityWarningModal } from './SharedWorkstationInactivityWarningModal';
import {
  DEVICE_STATUS_POLL_MS,
  loadInactivityTimeoutSeconds,
  parseActivityMs,
  useSharedWorkstationInactivityTimer,
} from './useSharedWorkstationInactivityTimer';

type InactivityContextValue = {
  readonly lockNow: (reason: OperatorSessionEndReason) => Promise<void>;
};

const InactivityContext = createContext<InactivityContextValue | null>(null);

export function SharedWorkstationInactivityProvider({
  children,
}: {
  readonly children: ReactNode;
}) {
  const { hasDevice, operatorSessionActive, refreshSessionStatus } =
    useSharedWorkstationOperatorSession();
  const lockRequired = useSharedWorkstationLockRequired();
  const enabled = hasDevice && operatorSessionActive && !lockRequired;

  const [timeoutSeconds, setTimeoutSeconds] = useState<number | null>(null);
  const [serverLastActivityMs, setServerLastActivityMs] = useState<number | null>(null);
  const [handoffBusy, setHandoffBusy] = useState(false);

  const onLock = useCallback(async () => {
    await refreshSessionStatus();
  }, [refreshSessionStatus]);

  const { state, secondsUntilLock, continueSession, lockNow } =
    useSharedWorkstationInactivityTimer({
      enabled,
      timeoutSeconds,
      serverLastActivityMs,
      onLock,
    });

  useEffect(() => {
    if (!enabled) {
      setTimeoutSeconds(null);
      setServerLastActivityMs(null);
      return;
    }
    let cancelled = false;
    const loadTimeout = async () => {
      const t = await loadInactivityTimeoutSeconds();
      if (!cancelled && t != null) setTimeoutSeconds(t);
    };
    void loadTimeout();
    const poll = window.setInterval(() => {
      void loadTimeout();
    }, DEVICE_STATUS_POLL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(poll);
    };
  }, [enabled]);

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;
    const syncServerActivity = async () => {
      const status = await fetchOperatorSessionStatus();
      if (cancelled || !status.ok) return;
      setServerLastActivityMs(parseActivityMs(status.last_activity_at));
      if (status.inactivity_timeout_seconds != null) {
        setTimeoutSeconds(status.inactivity_timeout_seconds);
      }
    };
    void syncServerActivity();
    const id = window.setInterval(() => {
      void syncServerActivity();
    }, 30_000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [enabled]);

  const endHandoff = useCallback(
    async (reason: OperatorSessionEndReason) => {
      setHandoffBusy(true);
      try {
        await lockNow(reason);
      } finally {
        setHandoffBusy(false);
      }
    },
    [lockNow],
  );

  const ctx = useMemo(() => ({ lockNow }), [lockNow]);

  return (
    <InactivityContext.Provider value={ctx}>
      {children}
      {enabled ? (
        <>
          <SharedWorkstationInactivityWarningModal
            opened={state === 'warning'}
            secondsUntilLock={secondsUntilLock}
            onContinue={continueSession}
            onLockNow={() => void lockNow('manual_lock')}
          />
          <SharedWorkstationHandoffToolbar onEndSession={(r) => void endHandoff(r)} busy={handoffBusy} />
        </>
      ) : null}
    </InactivityContext.Provider>
  );
}

export function useSharedWorkstationInactivity(): InactivityContextValue | null {
  return useContext(InactivityContext);
}
