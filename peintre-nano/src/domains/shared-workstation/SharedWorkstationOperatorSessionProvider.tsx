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
import { fetchOperatorSessionStatus, type OperatorSessionStatus } from '../../api/shared-workstation-operator-session-client';

export type SharedWorkstationOperatorSessionState = {
  readonly loading: boolean;
  readonly hasDevice: boolean;
  readonly operatorSessionActive: boolean;
  readonly overrideActive: boolean;
  readonly canActivateSuperAdminOverride: boolean;
  readonly overrideSecondsRemaining: number | null;
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
  const [overrideActive, setOverrideActive] = useState(false);
  const [canActivateSuperAdminOverride, setCanActivateSuperAdminOverride] = useState(false);
  const [overrideSecondsRemaining, setOverrideSecondsRemaining] = useState<number | null>(null);

  const refreshSessionStatus = useCallback(async (): Promise<boolean> => {
    if (!enabled) {
      setHasDevice(false);
      setOperatorSessionActive(false);
      setOverrideActive(false);
      setCanActivateSuperAdminOverride(false);
      setOverrideSecondsRemaining(null);
      setLoading(false);
      return false;
    }
    const enrolled = await hasDeviceIdentity();
    setHasDevice(enrolled);
    if (!enrolled) {
      setOperatorSessionActive(false);
      setOverrideActive(false);
      setCanActivateSuperAdminOverride(false);
      setOverrideSecondsRemaining(null);
      setLoading(false);
      return false;
    }
    const status: OperatorSessionStatus = await fetchOperatorSessionStatus();
    if (!status.ok) {
      setOperatorSessionActive(false);
      setOverrideActive(false);
      setCanActivateSuperAdminOverride(false);
      setOverrideSecondsRemaining(null);
      setLoading(false);
      return false;
    }
    setOperatorSessionActive(status.active);
    setOverrideActive(status.override_active);
    setCanActivateSuperAdminOverride(status.can_activate_super_admin_override);
    setOverrideSecondsRemaining(status.override_seconds_remaining);
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
      overrideActive,
      canActivateSuperAdminOverride,
      overrideSecondsRemaining,
      refreshSessionStatus,
    }),
    [
      loading,
      hasDevice,
      operatorSessionActive,
      overrideActive,
      canActivateSuperAdminOverride,
      overrideSecondsRemaining,
      refreshSessionStatus,
    ],
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

/** Variante sans provider (démo hors live-auth) — retourne `null`. */
export function useOptionalSharedWorkstationOperatorSession(): SharedWorkstationOperatorSessionState | null {
  return useContext(SharedWorkstationOperatorSessionContext);
}

/** Indique si le lock screen PIN doit masquer le shell métier. */
export function useSharedWorkstationLockRequired(): boolean {
  const ctx = useOptionalSharedWorkstationOperatorSession();
  if (!ctx) return false;
  const { loading, hasDevice, operatorSessionActive } = ctx;
  if (!hasDevice) return loading;
  return loading || !operatorSessionActive;
}

export async function probeDeviceIdentityPresent(): Promise<boolean> {
  const rec = await loadDeviceIdentity();
  return Boolean(rec?.device_id && rec?.device_secret);
}
