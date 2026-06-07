// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { ReceptionHistoryPanel } from '../../src/domains/reception/ReceptionHistoryPanel';
import { setReceptionPosteUiState } from '../../src/domains/reception/reception-poste-ui-state';
import '../../src/registry';

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

describe('Story 28.3 — hub historique réception', () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    setReceptionPosteUiState(false);
  });

  beforeEach(() => {
    setReceptionPosteUiState(false);
    vi.stubGlobal(
      'matchMedia',
      vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    );
    vi.stubGlobal(
      'ResizeObserver',
      class {
        observe(): void {}
        unobserve(): void {}
        disconnect(): void {}
      },
    );
  });

  it('affiche le panneau historique quand aucun poste n’est ouvert (hub inactif)', async () => {
    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u1' },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = requestUrl(input);
      if (url.includes('/v1/reception/tickets') && !/\/v1\/reception\/tickets\/[^/?]+/.test(url)) {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({
              tickets: [
                {
                  id: 'hist-1',
                  status: 'closed',
                  benevole_username: 'vol',
                  created_at: '2026-06-07T09:00:00Z',
                  total_lignes: 2,
                  total_poids: 1.5,
                },
              ],
              total: 1,
              page: 1,
              per_page: 20,
              total_pages: 1,
            }),
        } as Response);
      }
      return Promise.resolve({ ok: false, status: 404, text: async () => 'not found' } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <ReceptionHistoryPanel widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('reception-history-panel')).toBeTruthy();
    });
    expect(fetchMock).toHaveBeenCalled();
    expect(fetchMock.mock.calls.some(([input]) => requestUrl(input).includes('/v1/reception/tickets'))).toBe(true);
    expect(screen.getByTestId('reception-history-row-hist-1')).toBeTruthy();
  });

  it('masque le panneau historique quand un poste est ouvert (cockpit actif)', () => {
    setReceptionPosteUiState(true);
    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u1' },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <ReceptionHistoryPanel widgetProps={{}} />
      </RootProviders>,
    );

    expect(screen.queryByTestId('reception-history-panel')).toBeNull();
  });

  it('revient à la page 1 au retour hub après pagination et ouverture poste', async () => {
    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u1' },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = requestUrl(input);
      if (url.includes('/v1/reception/tickets') && !/\/v1\/reception\/tickets\/[^/?]+/.test(url)) {
        const pageMatch = /[?&]page=(\d+)/.exec(url);
        const requestedPage = pageMatch ? Number(pageMatch[1]) : 1;
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({
              tickets: [
                {
                  id: `hist-p${requestedPage}`,
                  status: 'closed',
                  benevole_username: 'vol',
                  created_at: '2026-06-07T09:00:00Z',
                  total_lignes: requestedPage,
                  total_poids: requestedPage,
                },
              ],
              total: 40,
              page: requestedPage,
              per_page: 20,
              total_pages: 2,
            }),
        } as Response);
      }
      return Promise.resolve({ ok: false, status: 404, text: async () => 'not found' } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <ReceptionHistoryPanel widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('reception-history-row-hist-p1')).toBeTruthy();
    });
    expect(screen.getByText(/page 1/)).toBeTruthy();

    fireEvent.click(screen.getByRole('button', { name: 'Page suiv.' }));

    await waitFor(() => {
      expect(screen.getByTestId('reception-history-row-hist-p2')).toBeTruthy();
    });
    expect(screen.getByText(/page 2/)).toBeTruthy();

    setReceptionPosteUiState(true);
    await waitFor(() => {
      expect(screen.queryByTestId('reception-history-panel')).toBeNull();
    });

    setReceptionPosteUiState(false);
    await waitFor(() => {
      expect(screen.getByTestId('reception-history-panel')).toBeTruthy();
    });
    await waitFor(() => {
      expect(screen.getByTestId('reception-history-row-hist-p1')).toBeTruthy();
    });
    expect(screen.getByText(/page 1/)).toBeTruthy();
    expect(screen.queryByTestId('reception-history-row-hist-p2')).toBeNull();

    const listCalls = fetchMock.mock.calls
      .map(([input]) => requestUrl(input))
      .filter((url) => url.includes('/v1/reception/tickets') && !/\/v1\/reception\/tickets\/[^/?]+/.test(url));
    expect(listCalls.some((url) => /[?&]page=1(?:&|$)/.test(url))).toBe(true);
    expect(listCalls[listCalls.length - 1]).toMatch(/[?&]page=1(?:&|$)/);
  });

  it('permet la pagination après retour hub depuis la page 1', async () => {
    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u1' },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = requestUrl(input);
      if (url.includes('/v1/reception/tickets') && !/\/v1\/reception\/tickets\/[^/?]+/.test(url)) {
        const pageMatch = /[?&]page=(\d+)/.exec(url);
        const requestedPage = pageMatch ? Number(pageMatch[1]) : 1;
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({
              tickets: [
                {
                  id: `hist-p${requestedPage}`,
                  status: 'closed',
                  benevole_username: 'vol',
                  created_at: '2026-06-07T09:00:00Z',
                  total_lignes: requestedPage,
                  total_poids: requestedPage,
                },
              ],
              total: 40,
              page: requestedPage,
              per_page: 20,
              total_pages: 2,
            }),
        } as Response);
      }
      return Promise.resolve({ ok: false, status: 404, text: async () => 'not found' } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <ReceptionHistoryPanel widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('reception-history-row-hist-p1')).toBeTruthy();
    });
    expect(screen.getByText(/page 1/)).toBeTruthy();

    setReceptionPosteUiState(true);
    await waitFor(() => {
      expect(screen.queryByTestId('reception-history-panel')).toBeNull();
    });

    setReceptionPosteUiState(false);
    await waitFor(() => {
      expect(screen.getByTestId('reception-history-panel')).toBeTruthy();
    });
    await waitFor(() => {
      expect(screen.getByTestId('reception-history-row-hist-p1')).toBeTruthy();
    });
    expect(screen.getByText(/page 1/)).toBeTruthy();

    fireEvent.click(screen.getByRole('button', { name: 'Page suiv.' }));

    await waitFor(() => {
      expect(screen.getByTestId('reception-history-row-hist-p2')).toBeTruthy();
    });
    expect(screen.getByText(/page 2/)).toBeTruthy();
  });
});
