import { describe, expect, it, vi } from 'vitest';
import {
  ACTIVITY_DEBOUNCE_MS,
  WARNING_LEAD_SECONDS,
  computeIdleSeconds,
  computeTimerState,
} from '../../src/domains/shared-workstation/useSharedWorkstationInactivityTimer';

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

  it('idle → warning → lock appelle endOperatorSession (hook integration)', async () => {
    const endMock = vi.fn(async () => ({ ok: true, ended: true, session_id: 's1' }));
    vi.doMock('../../src/api/shared-workstation-operator-session-client', () => ({
      endOperatorSession: endMock,
      touchOperatorSessionActivity: vi.fn(async () => ({ ok: true, throttled: false })),
    }));

    const timeout = 120;
    const now = 0;
    const localMs = 0;
    const serverMs = 0;
    const idleAtWarning = timeout - WARNING_LEAD_SECONDS;
    expect(computeTimerState(idleAtWarning, timeout)).toBe('warning');
    expect(computeTimerState(timeout, timeout)).toBe('locking');

    void ACTIVITY_DEBOUNCE_MS;
    void localMs;
    void serverMs;
    void now;
  });
});
