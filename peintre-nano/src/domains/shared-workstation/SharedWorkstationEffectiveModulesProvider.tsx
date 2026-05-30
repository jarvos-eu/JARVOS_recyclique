import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { fetchSharedWorkstationEffectiveModules } from '../../api/shared-workstation-effective-modules-client';
import { LIVE_AUTH_ACCESS_TOKEN_STORAGE_KEY } from '../../api/recyclique-auth-client';
import { useSharedWorkstationOperatorSession } from './SharedWorkstationOperatorSessionProvider';

function readAccessToken(): string | null {
  if (typeof sessionStorage === 'undefined') return null;
  const token = sessionStorage.getItem(LIVE_AUTH_ACCESS_TOKEN_STORAGE_KEY)?.trim();
  return token || null;
}

export type SharedWorkstationEffectiveModulesState = {
  readonly loading: boolean;
  readonly effectiveModuleKeys: readonly string[];
  readonly refreshEffectiveModules: () => Promise<readonly string[]>;
};

const SharedWorkstationEffectiveModulesContext =
  createContext<SharedWorkstationEffectiveModulesState | null>(null);

const POLL_MS = 30_000;

export function SharedWorkstationEffectiveModulesProvider({
  children,
}: {
  readonly children: ReactNode;
}) {
  const { hasDevice, operatorSessionActive } = useSharedWorkstationOperatorSession();
  const [loading, setLoading] = useState(true);
  const [effectiveModuleKeys, setEffectiveModuleKeys] = useState<readonly string[]>([]);

  const refreshEffectiveModules = useCallback(async (): Promise<readonly string[]> => {
    if (!hasDevice || !operatorSessionActive) {
      setEffectiveModuleKeys([]);
      setLoading(false);
      return [];
    }
    const token = readAccessToken();
    if (!token) {
      setEffectiveModuleKeys([]);
      setLoading(false);
      return [];
    }
    const result = await fetchSharedWorkstationEffectiveModules(token);
    if (!result.ok) {
      setEffectiveModuleKeys([]);
      setLoading(false);
      return [];
    }
    const keys = [...result.module_keys];
    setEffectiveModuleKeys(keys);
    setLoading(false);
    return keys;
  }, [hasDevice, operatorSessionActive]);

  useEffect(() => {
    void refreshEffectiveModules();
  }, [refreshEffectiveModules]);

  useEffect(() => {
    if (!hasDevice || !operatorSessionActive) return;
    const id = window.setInterval(() => {
      void refreshEffectiveModules();
    }, POLL_MS);
    return () => window.clearInterval(id);
  }, [hasDevice, operatorSessionActive, refreshEffectiveModules]);

  const value = useMemo(
    () => ({
      loading,
      effectiveModuleKeys,
      refreshEffectiveModules,
    }),
    [loading, effectiveModuleKeys, refreshEffectiveModules],
  );

  return (
    <SharedWorkstationEffectiveModulesContext.Provider value={value}>
      {children}
    </SharedWorkstationEffectiveModulesContext.Provider>
  );
}

export function useSharedWorkstationEffectiveModules(): SharedWorkstationEffectiveModulesState {
  const ctx = useContext(SharedWorkstationEffectiveModulesContext);
  if (!ctx) {
    return {
      loading: false,
      effectiveModuleKeys: [],
      refreshEffectiveModules: async () => [],
    };
  }
  return ctx;
}
