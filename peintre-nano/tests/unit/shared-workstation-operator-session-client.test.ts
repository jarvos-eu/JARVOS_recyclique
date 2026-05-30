import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  endOperatorSession,
  fetchOperatorSessionStatus,
  fetchSharedWorkstationDeviceStatus,
  touchOperatorSessionActivity,
} from '../../src/api/shared-workstation-operator-session-client';

vi.mock('../../src/domains/shared-workstation/device-identity-store', () => ({
  sharedWorkstationAuthHeaders: vi.fn(async () => ({
    'X-Recyclique-Device-Id': '660e8400-e29b-41d4-a716-446655440001',
    'X-Recyclique-Device-Credential': 'secret',
  })),
}));

describe('shared-workstation-operator-session-client', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('fetchOperatorSessionStatus parse champs enrichis et no-store', async () => {
    const fetchMock = vi.fn(async () =>
      Response.json({
        active: true,
        operator_user_id: '550e8400-e29b-41d4-a716-446655440000',
        session_id: '660e8400-e29b-41d4-a716-446655440001',
        last_activity_at: '2026-05-30T12:00:00Z',
        inactivity_timeout_seconds: 900,
        seconds_until_lock: 800,
      }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const result = await fetchOperatorSessionStatus();
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.inactivity_timeout_seconds).toBe(900);
      expect(result.seconds_until_lock).toBe(800);
    }
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(init.cache).toBe('no-store');
  });

  it('endOperatorSession POST reason manual_lock', async () => {
    const fetchMock = vi.fn(async () =>
      Response.json({ ended: true, session_id: '660e8400-e29b-41d4-a716-446655440001' }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const result = await endOperatorSession('manual_lock');
    expect(result.ok).toBe(true);
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(init.method).toBe('POST');
    expect(JSON.parse(init.body as string)).toEqual({ reason: 'manual_lock' });
    expect(init.cache).toBe('no-store');
  });

  it('touchOperatorSessionActivity POST activity', async () => {
    const fetchMock = vi.fn(async () => new Response(null, { status: 204 }));
    vi.stubGlobal('fetch', fetchMock);

    const result = await touchOperatorSessionActivity();
    expect(result.ok).toBe(true);
    expect(fetchMock.mock.calls[0]?.[0]).toContain('/operator-session/activity');
  });

  it('fetchSharedWorkstationDeviceStatus lit timeout', async () => {
    const fetchMock = vi.fn(async () =>
      Response.json({
        device_id: '660e8400-e29b-41d4-a716-446655440001',
        inactivity_timeout_seconds: 900,
      }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const result = await fetchSharedWorkstationDeviceStatus();
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.inactivity_timeout_seconds).toBe(900);
  });
});
