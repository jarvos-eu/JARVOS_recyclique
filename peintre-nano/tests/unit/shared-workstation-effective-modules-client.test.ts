import { describe, expect, it, vi, beforeEach } from 'vitest';
import { fetchSharedWorkstationEffectiveModules } from '../../src/api/shared-workstation-effective-modules-client';

const { sharedWorkstationAuthHeaders } = vi.hoisted(() => ({
  sharedWorkstationAuthHeaders: vi.fn(async () => ({
    'X-Recyclique-Device-Id': 'dev-1',
    'X-Recyclique-Device-Credential': 'secret',
  })),
}));

vi.mock('../../src/domains/shared-workstation/device-identity-store', () => ({
  sharedWorkstationAuthHeaders,
}));

vi.mock('../../src/api/live-snapshot-client', () => ({
  getLiveSnapshotBasePrefix: () => 'http://api.test',
}));

describe('shared-workstation-effective-modules-client', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    sharedWorkstationAuthHeaders.mockClear();
  });

  it('GET effective-modules avec Bearer, device headers et cache no-store', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({
          module_keys: ['kpi-live-banner'],
          computed_at: '2026-05-30T12:00:00Z',
          site_id: 's1',
          device_id: 'd1',
          operator_user_id: 'o1',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    );

    const result = await fetchSharedWorkstationEffectiveModules('token-abc');
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.module_keys).toEqual(['kpi-live-banner']);
    }

    expect(fetchMock).toHaveBeenCalledOnce();
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('http://api.test/v1/shared-workstation/effective-modules');
    expect(init.cache).toBe('no-store');
    expect((init.headers as Record<string, string>).Authorization).toBe('Bearer token-abc');
    expect((init.headers as Record<string, string>)['X-Recyclique-Device-Id']).toBe('dev-1');
  });
});
