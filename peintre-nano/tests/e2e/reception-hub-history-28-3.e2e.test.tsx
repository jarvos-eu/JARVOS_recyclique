// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { RuntimeDemoApp } from '../../src/app/demo/RuntimeDemoApp';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import '../../src/registry';
import '../../src/styles/tokens.css';

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    configurable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }),
  });
  globalThis.ResizeObserver = class {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  } as unknown as typeof ResizeObserver;
});

describe('E2E — Story 28.3 hub historique réception (REV-RECEPTION-01)', () => {
  const posteId = 'poste-hub-28-3-e2e';
  const ticketId = 'ticket-hub-28-3-e2e';

  beforeEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
    window.history.pushState({}, '', '/reception');
  });

  afterEach(() => {
    window.history.pushState({}, '', '/');
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
    cleanup();
  });

  it('liste hub visible, masquée en cockpit, réapparaît après fermeture poste (AC-HUB-HISTORY)', async () => {
    vi.stubEnv('VITE_LIVE_AUTH', 'true');
    let ticketStatus: 'opened' | 'closed' = 'opened';

    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();

      if (
        method === 'GET' &&
        url.includes('/v1/reception/tickets') &&
        !/\/v1\/reception\/tickets\/[^/?]+/.test(url)
      ) {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({
              tickets: [{ id: 'hist-1', status: 'closed', benevole_username: 'vol', created_at: '2026-06-07T09:00:00Z' }],
              total: 1,
              page: 1,
              per_page: 20,
              total_pages: 1,
            }),
        } as Response);
      }
      if (url.includes('/v1/reception/postes/open') && method === 'POST') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: posteId }),
        } as Response);
      }
      if (url.includes('/v1/reception/tickets') && method === 'POST' && !url.includes('/close')) {
        ticketStatus = 'opened';
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: ticketId }),
        } as Response);
      }
      if (url.includes(`/v1/reception/tickets/${ticketId}/close`) && method === 'POST') {
        ticketStatus = 'closed';
        return Promise.resolve({ ok: true, status: 200, text: async () => '{}' } as Response);
      }
      if (url.includes(`/v1/reception/tickets/${ticketId}`) && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({
              id: ticketId,
              poste_id: posteId,
              benevole_username: '',
              created_at: '',
              closed_at: ticketStatus === 'closed' ? '2026-06-07T11:00:00Z' : null,
              status: ticketStatus,
              lignes: [],
            }),
        } as Response);
      }
      if (url.includes(`/v1/reception/postes/${posteId}/close`) && method === 'POST') {
        return Promise.resolve({ ok: true, status: 200, text: async () => '{}' } as Response);
      }
      if (url.includes('/v1/reception/categories') && method === 'GET') {
        return Promise.resolve({ ok: true, status: 200, text: async () => '[]' } as Response);
      }
      if (url.includes('/v1/stats/live') && method === 'GET') {
        return Promise.resolve({ ok: true, status: 200, text: async () => '{}' } as Response);
      }
      return Promise.resolve({ ok: true, status: 200, text: async () => '{}' } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u-hub-28-3-e2e' },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <RuntimeDemoApp />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('reception-history-panel')).toBeTruthy();
    });
    expect(screen.getByTestId('reception-history-row-hist-1')).toBeTruthy();

    fireEvent.click(screen.getByTestId('reception-open-poste'));
    await waitFor(() => {
      expect(screen.getByTestId('reception-cockpit-layout')).toBeTruthy();
    });
    expect(screen.queryByTestId('reception-history-panel')).toBeNull();

    fireEvent.click(screen.getByTestId('reception-close-ticket'));
    await waitFor(() => {
      expect(screen.getByTestId('reception-close-poste')).toBeTruthy();
    });

    fireEvent.click(screen.getByTestId('reception-close-poste'));
    await waitFor(() => {
      expect(screen.getByTestId('reception-history-panel')).toBeTruthy();
    });
    expect(screen.queryByTestId('reception-cockpit-layout')).toBeNull();
    expect(screen.getByTestId('reception-return-to-menu')).toBeTruthy();
  });
});
