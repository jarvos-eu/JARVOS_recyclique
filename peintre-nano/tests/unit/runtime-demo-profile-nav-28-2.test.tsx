// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import '../../src/registry';
import '../../src/styles/tokens.css';
import { RuntimeDemoApp } from '../../src/app/demo/RuntimeDemoApp';
import { LiveAuthActionsProvider } from '../../src/app/auth/LiveAuthActionsContext';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';

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

afterEach(() => {
  cleanup();
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  window.history.pushState({}, '', '/');
});

describe('Story 28.2 — navigation menu → /profil', () => {
  it('ouvre le widget profil depuis le menu utilisateur live', async () => {
    vi.stubEnv('VITE_LIVE_AUTH', 'true');
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
        const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
        const method = (init?.method ?? 'GET').toUpperCase();
        const body = '{}';
        if (url.includes('/v1/users/me') && method === 'GET') {
          const me = {
            id: 'u-profile-nav',
            username: 'marie@example.com',
            first_name: 'Marie',
            last_name: 'Test',
            email: 'marie@example.com',
            role: 'user',
          };
          return Promise.resolve({
            ok: true,
            status: 200,
            text: async () => JSON.stringify(me),
            json: async () => me,
          } as Response);
        }
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => body,
          json: async () => JSON.parse(body),
        } as Response);
      }),
    );

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u-profile-nav', userDisplayLabel: 'Marie Test' },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    window.history.pushState({}, '', '/dashboard');

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <LiveAuthActionsProvider value={{ requestLogout: vi.fn() }}>
          <RuntimeDemoApp />
        </LiveAuthActionsProvider>
      </RootProviders>,
    );

    fireEvent.click(await screen.findByTestId('live-shell-user-menu-trigger'));
    await waitFor(() => {
      expect(screen.getByTestId('live-shell-user-menu-personal-dashboard')).toBeTruthy();
      expect(screen.getByTestId('live-shell-user-menu-profile')).toBeTruthy();
    });
    fireEvent.click(screen.getByTestId('live-shell-user-menu-profile'));

    await waitFor(() => {
      expect(window.location.pathname).toBe('/profil');
    });

    const main = screen.getByTestId('shell-zone-main');
    await waitFor(() => {
      expect(within(main).getByTestId('widget-user-self-profile')).toBeTruthy();
    });
  });
});
