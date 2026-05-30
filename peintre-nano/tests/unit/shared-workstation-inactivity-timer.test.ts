// @vitest-environment jsdom
import { act, render, waitFor } from '@testing-library/react';
import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import {
  ACTIVITY_DEBOUNCE_MS,
  type InjectableClock,
  type InactivityTimerState,
  WARNING_LEAD_SECONDS,
  computeIdleSeconds,
  computeTimerState,
  type UseSharedWorkstationInactivityTimerResult,
  useSharedWorkstationInactivityTimer,
} from '../../src/domains/shared-workstation/useSharedWorkstationInactivityTimer';

const { endOperatorSessionMock, touchOperatorSessionActivityMock } = vi.hoisted(() => ({
  endOperatorSessionMock: vi.fn(async () => ({ ok: true, ended: true, session_id: 's1' })),
  touchOperatorSessionActivityMock: vi.fn(async () => ({ ok: true, throttled: false })),
}));

vi.mock('../../src/api/shared-workstation-operator-session-client', () => ({
  endOperatorSession: endOperatorSessionMock,
  touchOperatorSessionActivity: touchOperatorSessionActivityMock,
  fetchSharedWorkstationDeviceStatus: vi.fn(async () => ({ ok: true, inactivity_timeout_seconds: 900 })),
}));

function createManualClock(startMs = 0): InjectableClock & { advance: (ms: number) => void } {
  let nowMs = startMs;
  let nextId = 1;
  const intervals = new Map<number, () => void>();
  const timeouts = new Map<number, { atMs: number; handler: () => void }>();

  return {
    now: () => nowMs,
    setInterval: (handler) => {
      const id = nextId++;
      intervals.set(id, handler);
      return id;
    },
    clearInterval: (id) => {
      intervals.delete(id);
    },
    setTimeout: (handler, timeout) => {
      const id = nextId++;
      timeouts.set(id, { atMs: nowMs + timeout, handler });
      return id;
    },
    clearTimeout: (id) => {
      timeouts.delete(id);
    },
    advance: (ms) => {
      nowMs += ms;
      for (const [id, timeout] of [...timeouts.entries()]) {
        if (timeout.atMs <= nowMs) {
          timeouts.delete(id);
          timeout.handler();
        }
      }
      for (const handler of intervals.values()) {
        handler();
      }
    },
  };
}

describe('shared-workstation-inactivity-timer', () => {
  it('computeIdleSeconds prend le max local/serveur (activité la plus récente)', () => {
    const now = 1_000_000;
    const idle = computeIdleSeconds({
      nowMs: now,
      localLastActivityMs: now - 5000,
      serverLastActivityMs: now - 2000,
    });
    expect(idle).toBe(2);
  });

  it('computeTimerState idle → warning → locking', () => {
    const timeout = 900;
    expect(computeTimerState(100, timeout)).toBe('idle');
    expect(computeTimerState(timeout - WARNING_LEAD_SECONDS, timeout)).toBe('warning');
    expect(computeTimerState(timeout, timeout)).toBe('locking');
  });

  it('horloge injectable: warning, continue repousse, puis timeout lock', async () => {
    endOperatorSessionMock.mockClear();
    touchOperatorSessionActivityMock.mockClear();

    const manualClock = createManualClock(0);
    const onLock = vi.fn(async () => {});
    let latest: UseSharedWorkstationInactivityTimerResult | null = null;

    function Harness() {
      const result = useSharedWorkstationInactivityTimer({
        enabled: true,
        timeoutSeconds: 90,
        serverLastActivityMs: 0,
        onLock,
        clock: manualClock,
      });
      latest = result;
      return null;
    }

    render(React.createElement(Harness));
    expect((latest?.state as InactivityTimerState) ?? null).toBe('idle');

    act(() => {
      manualClock.advance(31_000);
    });
    expect((latest?.state as InactivityTimerState) ?? null).toBe('warning');

    act(() => {
      latest?.continueSession();
    });
    expect((latest?.state as InactivityTimerState) ?? null).toBe('idle');

    act(() => {
      manualClock.advance(10_000);
    });
    expect((latest?.state as InactivityTimerState) ?? null).toBe('idle');

    act(() => {
      manualClock.advance(90_000);
    });

    await waitFor(() => {
      expect(endOperatorSessionMock).toHaveBeenCalledWith('timeout');
      expect(onLock).toHaveBeenCalledWith('timeout');
    });

    void ACTIVITY_DEBOUNCE_MS;
  });
});
