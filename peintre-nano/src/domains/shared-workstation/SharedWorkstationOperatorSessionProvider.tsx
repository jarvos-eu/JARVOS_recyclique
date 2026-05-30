import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { hasDeviceIdentity, loadDeviceIdentity } from './device-identity-store';
import {
  fetchOperatorSessionStatus,
  type OperatorSessionStatus,
} from '../../api/shared-workstation-operator-pin-client';

export type SharedWorkstationOperatorSessionState = {
  readonly loading: boolean;
  readonly hasDevice: boolean;
  readonly operatorSessionActive: boolean;
  readonly refreshSessionStatus: () => Promise<boolean>;
};

const SharedWorkstationOperatorSessionContext =
  createContext<SharedWorkstationOperatorSessionState | null>(null);

const POLL_MS = 30_000;

export function SharedWorkstationOperatorSessionProvider({
  children,
  enabled,
}: {
  readonly children: ReactNode;
  readonly enabled: boolean;
}) {
  const [loading, setLoading] = useState(true);
  const [hasDevice, setHasDevice] = useState(false);
  const [operatorSessionActive, setOperatorSessionActive] = useState(false);

  const refreshSessionStatus = useCallback(async (): Promise<boolean> => {
    if (!enabled) {
      setHasDevice(false);
      setOperatorSessionActive(false);
      setLoading(false);
      return false;
    }
    const enrolled = await hasDeviceIdentity();
    setHasDevice(enrolled);
    if (!enrolled) {
      setOperatorSessionActive(false);
      setLoading(false);
      return false;
    }
    const status: OperatorSessionStatus = await fetchOperatorSessionStatus();
    if (!status.ok) {
      setOperatorSessionActive(false);
      setLoading(false);
      return false;
    }
    setOperatorSessionActive(status.active);
    setLoading(false);
    return status.active;
  }, [enabled]);

  useEffect(() => {
    void refreshSessionStatus();
  }, [refreshSessionStatus]);

  useEffect(() => {
    if (!enabled || !hasDevice) return;
    const id = window.setInterval(() => {
      void refreshSessionStatus();
    }, POLL_MS);
    return () => window.clearInterval(id);
  }, [enabled, hasDevice, refreshSessionStatus]);

  const value = useMemo(
    () => ({
      loading,
      hasDevice,
      operatorSessionActive,
      refreshSessionStatus,
    }),
    [loading, hasDevice, operatorSessionActive, refreshSessionStatus],
  );

  return (
    <SharedWorkstationOperatorSessionContext.Provider value={value}>
      {children}
    </SharedWorkstationOperatorSessionContext.Provider>
  );
}

export function useSharedWorkstationOperatorSession(): SharedWorkstationOperatorSessionState {
  const ctx = useContext(SharedWorkstationOperatorSessionContext);
  if (!ctx) {
    throw new Error('useSharedWorkstationOperatorSession requires provider');
  }
  return ctx;
}

/** Indique si le lock screen PIN doit masquer le shell métier. */
export function useSharedWorkstationLockRequired(): boolean {
  const { loading, hasDevice, operatorSessionActive } = useSharedWorkstationOperatorSession();
  if (!hasDevice) return false;
  return loading || !operatorSessionActive;
}

export async function probeDeviceIdentityPresent(): Promise<boolean> {
  const rec = await loadDeviceIdentity();
  return Boolean(rec?.device_id && rec?.device_secret);
}
