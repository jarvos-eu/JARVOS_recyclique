import { describe, expect, it, vi, beforeEach } from 'vitest';
import {
  abandonSharedWorkstationReceptionDraft,
  fetchSharedWorkstationReceptionDraft,
  resumeSharedWorkstationReceptionDraft,
} from '../../src/api/shared-workstation-reception-draft-client';

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

describe('shared-workstation-reception-draft-client', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    sharedWorkstationAuthHeaders.mockClear();
  });

  it('GET reception-draft avec Bearer, device headers et cache no-store', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({
          summary: {
            poste_id: 'p1',
            ticket_id: 't1',
            started_by_display: 'Alice',
            started_at: '2026-05-30T10:00:00.000Z',
            line_count: 0,
          },
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    );

    const result = await fetchSharedWorkstationReceptionDraft('token-abc');
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.summary?.poste_id).toBe('p1');
    }

    expect(fetchMock).toHaveBeenCalledOnce();
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('http://api.test/v1/shared-workstation/reception-draft');
    expect(init.method).toBe('GET');
    expect(init.cache).toBe('no-store');
    expect((init.headers as Record<string, string>).Authorization).toBe('Bearer token-abc');
    expect((init.headers as Record<string, string>)['X-Recyclique-Device-Id']).toBe('dev-1');
  });

  it('POST resume et abandon avec cache no-store et confirm true', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({ poste_id: 'p1', ticket_id: 't1' }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        ),
      )
      .mockResolvedValueOnce(new Response('', { status: 200 }));

    const resume = await resumeSharedWorkstationReceptionDraft('token-abc');
    expect(resume.ok).toBe(true);

    const abandon = await abandonSharedWorkstationReceptionDraft('token-abc');
    expect(abandon.ok).toBe(true);

    expect(fetchMock).toHaveBeenCalledTimes(2);

    const [, resumeInit] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(resumeInit.method).toBe('POST');
    expect(resumeInit.cache).toBe('no-store');
    expect(JSON.parse(String(resumeInit.body))).toEqual({ confirm: true });

    const [abandonUrl, abandonInit] = fetchMock.mock.calls[1] as [string, RequestInit];
    expect(abandonUrl).toBe('http://api.test/v1/shared-workstation/reception-draft/abandon');
    expect(abandonInit.cache).toBe('no-store');
    expect(JSON.parse(String(abandonInit.body))).toEqual({ confirm: true });
  });
});
