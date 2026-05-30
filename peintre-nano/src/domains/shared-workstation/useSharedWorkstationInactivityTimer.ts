import { useCallback, useEffect, useRef, useState } from 'react';
import {
  endOperatorSession,
  fetchSharedWorkstationDeviceStatus,
  touchOperatorSessionActivity,
  type OperatorSessionEndReason,
} from '../../api/shared-workstation-operator-session-client';

/** Fenêtre avertissement avant verrouillage (~1 min). */
export const WARNING_LEAD_SECONDS = 60;

/** Debounce événements activité UI. */
export const ACTIVITY_DEBOUNCE_MS = 1000;

/** Throttle heartbeat serveur côté client (aligné back 30 s). */
export const HEARTBEAT_MIN_INTERVAL_MS = 30_000;

/** Rafraîchissement policy timeout admin. */
export const DEVICE_STATUS_POLL_MS = 5 * 60 * 1000;

export const TICK_INTERVAL_MS = 1000;

export type InactivityTimerState = 'idle' | 'warning' | 'locking';

export type InjectableClock = {
  readonly now: () => number;
  readonly setInterval: (handler: () => void, timeout: number) => number;
  readonly clearInterval: (id: number) => void;
  readonly setTimeout?: (handler: () => void, timeout: number) => number;
  readonly clearTimeout?: (id: number) => void;
};

export const defaultClock: InjectableClock = {
  now: () => Date.now(),
  setInterval: (fn, ms) => window.setInterval(fn, ms),
  clearInterval: (id) => window.clearInterval(id),
  setTimeout: (fn, ms) => window.setTimeout(fn, ms),
  clearTimeout: (id) => window.clearTimeout(id),
};

export type UseSharedWorkstationInactivityTimerOptions = {
  readonly enabled: boolean;
  readonly timeoutSeconds: number | null;
  readonly serverLastActivityMs: number | null;
  readonly onLock: (reason: OperatorSessionEndReason) => Promise<void>;
  readonly clock?: InjectableClock;
};

export type UseSharedWorkstationInactivityTimerResult = {
  readonly state: InactivityTimerState;
  readonly secondsUntilLock: number | null;
  readonly continueSession: () => void;
  readonly lockNow: (reason: OperatorSessionEndReason) => Promise<void>;
};

export function parseActivityMs(iso: string | null): number | null {
  if (!iso) return null;
  const ms = Date.parse(iso);
  return Number.isFinite(ms) ? ms : null;
}

export function computeIdleSeconds(options: {
  nowMs: number;
  localLastActivityMs: number;
  serverLastActivityMs: number | null;
}): number {
  const { nowMs, localLastActivityMs, serverLastActivityMs } = options;
  const serverMs = serverLastActivityMs ?? localLastActivityMs;
  const lastMs = Math.max(localLastActivityMs, serverMs);
  return Math.max(0, (nowMs - lastMs) / 1000);
}

export function computeTimerState(
  idleSeconds: number,
  timeoutSeconds: number,
): InactivityTimerState {
  if (idleSeconds >= timeoutSeconds) return 'locking';
  if (idleSeconds >= timeoutSeconds - WARNING_LEAD_SECONDS) return 'warning';
  return 'idle';
}

export function useSharedWorkstationInactivityTimer(
  options: UseSharedWorkstationInactivityTimerOptions,
): UseSharedWorkstationInactivityTimerResult {
  const clock = options.clock ?? defaultClock;
  const { enabled, timeoutSeconds, serverLastActivityMs, onLock } = options;

  const localActivityRef = useRef(clock.now());
  const lastHeartbeatRef = useRef(0);
  const lockingRef = useRef(false);
  const debounceRef = useRef<number | null>(null);

  const [state, setState] = useState<InactivityTimerState>('idle');
  const [secondsUntilLock, setSecondsUntilLock] = useState<number | null>(null);

  const bumpLocalActivity = useCallback(() => {
    const now = clock.now();
    localActivityRef.current = now;
    if (now - lastHeartbeatRef.current >= HEARTBEAT_MIN_INTERVAL_MS) {
      lastHeartbeatRef.current = now;
      void touchOperatorSessionActivity();
    }
  }, [clock]);

  const continueSession = useCallback(() => {
    bumpLocalActivity();
    setState('idle');
  }, [bumpLocalActivity]);

  const lockNow = useCallback(
    async (reason: OperatorSessionEndReason) => {
      if (lockingRef.current) return;
      lockingRef.current = true;
      setState('locking');
      try {
        await endOperatorSession(reason);
        await onLock(reason);
      } finally {
        lockingRef.current = false;
      }
    },
    [onLock],
  );

  useEffect(() => {
    if (!enabled || timeoutSeconds == null || timeoutSeconds <= 0) {
      setState('idle');
      setSecondsUntilLock(null);
      return;
    }

    localActivityRef.current = clock.now();

    const tick = () => {
      const now = clock.now();
      const idle = computeIdleSeconds({
        nowMs: now,
        localLastActivityMs: localActivityRef.current,
        serverLastActivityMs,
      });
      const nextState = computeTimerState(idle, timeoutSeconds);
      setSecondsUntilLock(Math.max(0, Math.ceil(timeoutSeconds - idle)));
      setState(nextState);
      if (nextState === 'locking' && !lockingRef.current) {
        void lockNow('timeout');
      }
    };

    tick();
    const id = clock.setInterval(tick, TICK_INTERVAL_MS);
    return () => clock.clearInterval(id);
  }, [clock, enabled, timeoutSeconds, serverLastActivityMs, lockNow]);

  useEffect(() => {
    if (!enabled) return;

    const onActivity = () => {
      if (debounceRef.current != null) {
        clock.clearTimeout?.(debounceRef.current);
      }
      debounceRef.current = clock.setTimeout?.(() => {
        bumpLocalActivity();
        debounceRef.current = null;
      }, ACTIVITY_DEBOUNCE_MS) ?? null;
    };

    const events: Array<keyof WindowEventMap> = [
      'keydown',
      'pointerdown',
      'touchstart',
      'click',
    ];
    for (const ev of events) {
      window.addEventListener(ev, onActivity, { passive: true });
    }
    return () => {
      for (const ev of events) {
        window.removeEventListener(ev, onActivity);
      }
      if (debounceRef.current != null) {
        clock.clearTimeout?.(debounceRef.current);
      }
    };
  }, [enabled, bumpLocalActivity, clock]);

  return { state, secondsUntilLock, continueSession, lockNow };
}

export async function loadInactivityTimeoutSeconds(): Promise<number | null> {
  const status = await fetchSharedWorkstationDeviceStatus();
  if (!status.ok) return null;
  return status.inactivity_timeout_seconds;
}
