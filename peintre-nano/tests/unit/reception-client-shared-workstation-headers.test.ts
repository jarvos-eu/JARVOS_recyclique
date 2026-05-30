import { afterEach, describe, expect, it, vi } from 'vitest';
import { postOpenPoste } from '../../src/api/reception-client';

vi.mock('../../src/domains/shared-workstation/device-identity-store', () => ({
  sharedWorkstationAuthHeaders: vi.fn(async () => ({
    'X-Recyclique-Device-Id': '660e8400-e29b-41d4-a716-446655440001',
    'X-Recyclique-Device-Credential': 'device-secret-27-8',
  })),
}));

vi.mock('../../src/api/live-snapshot-client', () => ({
  getLiveSnapshotBasePrefix: () => 'http://api.test',
}));

import { sharedWorkstationAuthHeaders } from '../../src/domains/shared-workstation/device-identity-store';

describe('reception-client — en-têtes poste partagé (Story 27.8)', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('postOpenPoste propage sharedWorkstationAuthHeaders sur POST /postes/open', async () => {
    const fetchMock = vi.fn(async () =>
      Response.json({ id: 'poste-1', status: 'opened' }, { status: 200 }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const auth = { getAccessToken: () => 'jwt-token-27-8' };
    const result = await postOpenPoste(auth);
    expect(result.ok).toBe(true);

    expect(sharedWorkstationAuthHeaders).toHaveBeenCalled();

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('http://api.test/v1/reception/postes/open');
    expect(init.method).toBe('POST');
    const headers = init.headers as Record<string, string>;
    expect(headers.Authorization).toBe('Bearer jwt-token-27-8');
    expect(headers['X-Recyclique-Device-Id']).toBe('660e8400-e29b-41d4-a716-446655440001');
    expect(headers['X-Recyclique-Device-Credential']).toBe('device-secret-27-8');
  });
});
