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

function buildReceptionHubFetchMock() {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = requestUrl(input);
    const method = (init?.method ?? 'GET').toUpperCase();

    if (url.includes('/v1/reception/categories') && method === 'GET') {
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '[]',
        json: async () => [],
      } as Response);
    }
    if (url.includes('/v1/stats/live') && method === 'GET') {
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '{}',
        json: async () => ({}),
      } as Response);
    }
    return Promise.resolve({
      ok: true,
      status: 200,
      text: async () => '{}',
      json: async () => ({}),
    } as Response);
  });
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

describe('E2E — Story 28.2 sortie PWA réception hub inactif (REV-RECEPTION-02)', () => {
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

  it('masque la nav shell sur /reception puis Retour au menu → /dashboard (AC-PWA-EXIT)', async () => {
    vi.stubEnv('VITE_LIVE_AUTH', 'true');
    vi.stubGlobal('fetch', buildReceptionHubFetchMock());

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u-reception-exit-28-2' },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <RuntimeDemoApp />
      </RootProviders>,
    );

    const shell = await screen.findByTestId('peintre-nano-shell');
    expect(shell.getAttribute('data-pn-kiosk-nav-hidden')).toBe('true');
    expect(screen.queryByTestId('shell-zone-nav')).toBeNull();

    const returnBtn = await screen.findByTestId('reception-return-to-menu');
    expect(returnBtn.textContent).toMatch(/Retour au menu/i);
    fireEvent.click(returnBtn);

    await waitFor(() => {
      expect(window.location.pathname).toBe('/dashboard');
    });

    await waitFor(() => {
      expect(screen.getByTestId('shell-zone-nav')).toBeTruthy();
    });
    expect(screen.getByTestId('peintre-nano-shell').getAttribute('data-pn-kiosk-nav-hidden')).toBeNull();
  });
});
