import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  fetchOperatorSessionStatus,
  verifySharedWorkstationOperatorPin,
} from '../../src/api/shared-workstation-operator-pin-client';

vi.mock('../../src/domains/shared-workstation/device-identity-store', () => ({
  sharedWorkstationAuthHeaders: vi.fn(async () => ({
    'X-Recyclique-Device-Id': '660e8400-e29b-41d4-a716-446655440001',
    'X-Recyclique-Device-Credential': 'secret',
  })),
}));

import { sharedWorkstationAuthHeaders } from '../../src/domains/shared-workstation/device-identity-store';

describe('shared-workstation-operator-pin-client', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('fetchOperatorSessionStatus envoie les en-têtes device et no-store', async () => {
    const fetchMock = vi.fn(async () =>
      Response.json({ active: false, operator_user_id: null, session_id: null }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const result = await fetchOperatorSessionStatus();
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.active).toBe(false);

    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(init.cache).toBe('no-store');
    const headers = init.headers as Record<string, string>;
    expect(headers['X-Recyclique-Device-Id']).toBeTruthy();
    expect(headers['X-Recyclique-Device-Credential']).toBeTruthy();
  });

  it('verifySharedWorkstationOperatorPin ne log pas le PIN', async () => {
    const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    const fetchMock = vi.fn(async () =>
      Response.json({
        session_id: 'a',
        device_id: 'b',
        operator_user_id: 'c',
        site_id: 'd',
        started_at: '2026-05-30T12:00:00Z',
      }),
    );
    vi.stubGlobal('fetch', fetchMock);

    await verifySharedWorkstationOperatorPin({
      operator_user_id: '550e8400-e29b-41d4-a716-446655440000',
      pin: '1234',
    });

    const body = (fetchMock.mock.calls[0]?.[1] as RequestInit).body as string;
    expect(body).toContain('1234');
    expect(logSpy).not.toHaveBeenCalledWith(expect.stringContaining('1234'));
    logSpy.mockRestore();
  });

  it('sharedWorkstationAuthHeaders est invoqué', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => Response.json({ active: true })));
    await fetchOperatorSessionStatus();
    expect(sharedWorkstationAuthHeaders).toHaveBeenCalled();
  });
});
