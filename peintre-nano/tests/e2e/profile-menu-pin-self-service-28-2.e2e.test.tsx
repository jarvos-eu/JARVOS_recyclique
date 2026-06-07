// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { RuntimeDemoApp } from '../../src/app/demo/RuntimeDemoApp';
import { LiveAuthActionsProvider } from '../../src/app/auth/LiveAuthActionsContext';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import '../../src/registry';
import '../../src/styles/tokens.css';

const USER_ID = 'u-profile-e2e-28-2';

const meProfile = {
  id: USER_ID,
  username: 'marie@example.com',
  first_name: 'Marie',
  last_name: 'Test',
  email: 'marie@example.com',
  role: 'user',
};

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

function buildProfileFetchMock(pinPutHandler?: (body: string) => Response | Promise<Response>) {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = requestUrl(input);
    const method = (init?.method ?? 'GET').toUpperCase();

    if (url.includes('/v1/users/me/pin') && method === 'PUT') {
      const rawBody = init?.body != null ? String(init.body) : '{}';
      if (pinPutHandler) return Promise.resolve(pinPutHandler(rawBody));
      const pinBody = JSON.stringify({ message: 'PIN successfully set' });
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => pinBody,
        json: async () => JSON.parse(pinBody),
      } as Response);
    }

    if (url.includes('/v1/users/me') && method === 'GET') {
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => JSON.stringify(meProfile),
        json: async () => meProfile,
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

function renderLiveRuntimeDemo() {
  const auth = createMockAuthAdapter({
    session: { authenticated: true, userId: USER_ID, userDisplayLabel: 'Marie Test' },
    envelope: createDefaultDemoEnvelope(),
    accessToken: 'tok',
  });

  return render(
    <RootProviders authAdapter={auth} disableUserPrefsPersistence>
      <LiveAuthActionsProvider value={{ requestLogout: vi.fn() }}>
        <RuntimeDemoApp />
      </LiveAuthActionsProvider>
    </RootProviders>,
  );
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

describe('E2E — Story 28.2 profil menu + PIN self-service', () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
    window.history.pushState({}, '', '/dashboard');
  });

  afterEach(() => {
    window.history.pushState({}, '', '/');
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
    cleanup();
  });

  it('menu live Mon profil → /profil rend le widget self-service (AC-MENU, AC-PROFIL-ROUTE)', async () => {
    vi.stubEnv('VITE_LIVE_AUTH', 'true');
    vi.stubGlobal('fetch', buildProfileFetchMock());

    renderLiveRuntimeDemo();

    fireEvent.click(await screen.findByTestId('live-shell-user-menu-trigger'));
    await waitFor(() => {
      expect(screen.getByTestId('live-shell-user-menu-profile')).toBeTruthy();
    });
    fireEvent.click(screen.getByTestId('live-shell-user-menu-profile'));

    await waitFor(() => {
      expect(window.location.pathname).toBe('/profil');
    });

    const main = screen.getByTestId('shell-zone-main');
    await waitFor(() => {
      expect(within(main).getByTestId('widget-user-self-profile')).toBeTruthy();
      expect(within(main).getByRole('heading', { name: /Mon profil/i })).toBeTruthy();
    });
  });

  it('parcours e2e : menu → profil → premier PIN via PUT /v1/users/me/pin (AC-PIN-SELF-SERVICE)', async () => {
    vi.stubEnv('VITE_LIVE_AUTH', 'true');
    const fetchMock = buildProfileFetchMock();
    vi.stubGlobal('fetch', fetchMock);

    renderLiveRuntimeDemo();

    fireEvent.click(await screen.findByTestId('live-shell-user-menu-trigger'));
    fireEvent.click(await screen.findByTestId('live-shell-user-menu-profile'));

    await waitFor(() => {
      expect(window.location.pathname).toBe('/profil');
    });

    const main = screen.getByTestId('shell-zone-main');
    await waitFor(() => within(main).getByTestId('user-profile-pin-section'));

    fireEvent.change(within(main).getByTestId('user-profile-pin-input'), { target: { value: '1234' } });
    fireEvent.change(within(main).getByTestId('user-profile-pin-confirm-input'), {
      target: { value: '1234' },
    });
    fireEvent.click(within(main).getByTestId('user-profile-pin-submit'));

    await waitFor(() => {
      expect(within(main).getByTestId('user-profile-pin-success')).toBeTruthy();
    });

    const pinPut = fetchMock.mock.calls.find(([inp, init]) => {
      const url = requestUrl(inp as RequestInfo);
      const method = (init?.method ?? 'GET').toUpperCase();
      return url.includes('/v1/users/me/pin') && method === 'PUT';
    });
    expect(pinPut).toBeTruthy();
    const putBody = JSON.parse(String(pinPut![1]?.body));
    expect(putBody).toEqual({ pin: '1234' });
  });
});
