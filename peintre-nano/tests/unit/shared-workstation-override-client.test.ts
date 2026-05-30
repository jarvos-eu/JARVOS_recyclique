import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  activateOverride,
  deactivateOverride,
} from '../../src/api/shared-workstation-override-client';

vi.mock('../../src/domains/shared-workstation/device-identity-store', () => ({
  sharedWorkstationAuthHeaders: vi.fn(async () => ({
    'X-Recyclique-Device-Id': '660e8400-e29b-41d4-a716-446655440001',
    'X-Recyclique-Device-Credential': 'secret',
  })),
}));

describe('shared-workstation-override-client', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('activateOverride POST confirmation_pin avec no-store', async () => {
    const fetchMock = vi.fn(async () =>
      Response.json({
        override_active: true,
        override_started_at: '2026-05-30T12:00:00Z',
        override_expires_at: '2026-05-30T12:30:00Z',
      }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const result = await activateOverride('4242');
    expect(result.ok).toBe(true);
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(fetchMock.mock.calls[0]?.[0]).toContain('/override/activate');
    expect(init.method).toBe('POST');
    expect(init.cache).toBe('no-store');
    expect(JSON.parse(init.body as string)).toEqual({ confirmation_pin: '4242' });
  });

  it('deactivateOverride POST reason user_exit', async () => {
    const fetchMock = vi.fn(async () => Response.json({ override_active: false }));
    vi.stubGlobal('fetch', fetchMock);

    const result = await deactivateOverride('user_exit');
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.override_active).toBe(false);
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(fetchMock.mock.calls[0]?.[0]).toContain('/override/deactivate');
    expect(JSON.parse(init.body as string)).toEqual({ reason: 'user_exit' });
    expect(init.cache).toBe('no-store');
  });
});
