import { afterEach, describe, expect, it, vi } from 'vitest';
import { listRegisteredDevicesForAdmin } from '../../src/api/admin-registered-devices-client';

describe('admin-registered-devices-client — URL liste', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('appelle GET /v1/registered-devices/ (slash avant la query)', async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      text: async () => '[]',
    });
    vi.stubGlobal('fetch', fetchSpy);

    const auth = { getAccessToken: () => undefined as string | undefined };
    await listRegisteredDevicesForAdmin(auth, { limit: 10 });

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    const calledUrl = fetchSpy.mock.calls[0][0] as string;
    expect(calledUrl).toContain('/v1/registered-devices/?');
    expect(calledUrl).not.toContain('/v1/registered-devices?limit');
  });

  it('sans query conserve le slash final', async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      text: async () => '[]',
    });
    vi.stubGlobal('fetch', fetchSpy);

    const auth = { getAccessToken: () => undefined as string | undefined };
    await listRegisteredDevicesForAdmin(auth, {});

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    const calledUrl = fetchSpy.mock.calls[0][0] as string;
    expect(calledUrl.endsWith('/v1/registered-devices/')).toBe(true);
  });
});
