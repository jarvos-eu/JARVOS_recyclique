// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from '../../src/app/App';
import { RootProviders } from '../../src/app/providers/RootProviders';
import {
  hasDeviceIdentity,
  saveDeviceIdentity,
} from '../../src/domains/shared-workstation/device-identity-store';
import { LIVE_AUTH_ACCESS_TOKEN_STORAGE_KEY } from '../../src/api/recyclique-auth-client';
import '../../src/registry';
import '../../src/styles/tokens.css';

const siteId = '550e8400-e29b-41d4-a716-446655440000';
const deviceId = '660e8400-e29b-41d4-a716-446655440001';
const operatorUserId = '770e8400-e29b-41d4-a716-446655440002';

type StoreRecord = Record<string, unknown>;
const memoryStore = new Map<string, StoreRecord>();

function makeRequest<T>(result: T): IDBRequest<T> {
  const req = {
    result,
    error: null as DOMException | null,
    onsuccess: null as ((ev: Event) => void) | null,
    onerror: null as ((ev: Event) => void) | null,
  } as IDBRequest<T>;
  queueMicrotask(() => req.onsuccess?.(new Event('success')));
  return req;
}

function installIndexedDbMock() {
  memoryStore.clear();
  vi.stubGlobal('indexedDB', {
    open: () => {
      const db = {
        objectStoreNames: { contains: () => false },
        createObjectStore: () => ({}),
        transaction: () => ({
          objectStore: () => ({
            get: (key: IDBValidKey) => makeRequest(memoryStore.get(String(key))),
            put: (value: StoreRecord, key: IDBValidKey) => {
              memoryStore.set(String(key), value);
              return makeRequest(key);
            },
            delete: (key: IDBValidKey) => {
              memoryStore.delete(String(key));
              return makeRequest(undefined);
            },
          }),
        }),
        close: () => undefined,
      } as unknown as IDBDatabase;
      const req = {
        result: db,
        onsuccess: null as ((ev: Event) => void) | null,
        onupgradeneeded: null as ((ev: IDBOpenDBRequestEventMap['upgradeneeded']) => void) | null,
      } as IDBOpenDBRequest;
      queueMicrotask(() => {
        req.onupgradeneeded?.({ target: req } as IDBVersionChangeEvent);
        req.onsuccess?.(new Event('success'));
      });
      return req;
    },
  });
}

type EffectiveModulesMode = 'with-banner' | 'empty' | 'forbidden';

function buildContextEnvelopeBody(effectiveModuleKeys?: readonly string[] | null) {
  const body: Record<string, unknown> = {
    runtime_state: 'ok',
    permission_keys: [
      'transverse.dashboard.view',
      'recyclique.exploitation.view-live-band',
    ],
    computed_at: '2026-05-30T12:00:00.000Z',
    presentation_labels: {
      'nav.transverse.dashboard': 'Tableau de bord',
    },
    context: {
      site_id: siteId,
      cash_register_id: null,
      cash_session_id: null,
      reception_post_id: null,
    },
  };
  if (effectiveModuleKeys !== undefined) {
    body.effective_module_keys = effectiveModuleKeys;
  }
  return body;
}

function createLiveAuthFetchMock(options: { effectiveModules?: EffectiveModulesMode } = {}) {
  let operatorSessionActive = false;
  const effectiveModules = options.effectiveModules ?? 'with-banner';

  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const method = (init?.method ?? 'GET').toUpperCase();

    if (url.includes('/v1/users/me/context') && (method === 'GET' || method === 'POST')) {
      return new Response(JSON.stringify(buildContextEnvelopeBody(null)), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    if (url.includes('/shared-workstation/operator-session/status') && method === 'GET') {
      return new Response(
        JSON.stringify({
          active: operatorSessionActive,
          operator_user_id: operatorSessionActive ? operatorUserId : null,
          session_id: operatorSessionActive ? 'sess-e2e-27-7' : null,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    }

    if (url.includes('/shared-workstation/effective-modules') && method === 'GET') {
      if (effectiveModules === 'forbidden') {
        return new Response(
          JSON.stringify({
            code: 'SHARED_WORKSTATION_OPERATOR_REQUIRED',
            message: 'Session opérateur requise',
          }),
          { status: 403, headers: { 'Content-Type': 'application/json' } },
        );
      }
      const module_keys =
        effectiveModules === 'empty' ? [] : ['kpi-live-banner'];
      return new Response(
        JSON.stringify({
          module_keys,
          computed_at: '2026-05-30T12:00:00.000Z',
          site_id: siteId,
          device_id: deviceId,
          operator_user_id: operatorUserId,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    }

    if (url.includes('/shared-workstation/operator-pin/verify') && method === 'POST') {
      operatorSessionActive = true;
      return new Response(
        JSON.stringify({
          session_id: 'sess-e2e-27-7',
          device_id: deviceId,
          operator_user_id: operatorUserId,
          site_id: siteId,
          started_at: '2026-05-30T12:00:00Z',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    }

    if (url.includes('/module-config/') && method === 'GET') {
      return new Response(
        JSON.stringify({ schema_version: 1, payload: {}, version: 0 }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    }

    return new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } });
  });

  return fetchMock;
}

function renderLiveAuthApp() {
  vi.stubEnv('VITE_LIVE_AUTH', 'true');
  sessionStorage.setItem(LIVE_AUTH_ACCESS_TOKEN_STORAGE_KEY, 'e2e-live-auth-token-27-7');
  window.history.pushState({}, '', '/dashboard');
  return render(
    <RootProviders>
      <App />
    </RootProviders>,
  );
}

function fillOperatorPinForm(pin = '4242') {
  fireEvent.change(screen.getByTestId('shared-workstation-operator-id'), {
    target: { value: operatorUserId },
  });
  const pinRoot = screen.getByTestId('shared-workstation-pin-input');
  const inputs = pinRoot.querySelectorAll('input');
  pin.split('').forEach((digit, i) => {
    fireEvent.change(inputs[i]!, { target: { value: digit } });
  });
}

async function unlockWithPin(fetchMock: ReturnType<typeof createLiveAuthFetchMock>) {
  await waitFor(() => {
    expect(screen.getByTestId('shared-workstation-lock-screen')).toBeTruthy();
  });
  fillOperatorPinForm();
  fireEvent.click(screen.getByTestId('shared-workstation-pin-submit'));
  await waitFor(() => {
    expect(screen.queryByTestId('shared-workstation-lock-screen')).toBeNull();
  });
  await waitFor(() => {
    expect(
      fetchMock.mock.calls.some((c) => String(c[0]).includes('/effective-modules')),
    ).toBe(true);
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
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }),
  });
  globalThis.ResizeObserver = class ResizeObserver {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  } as unknown as typeof ResizeObserver;
});

beforeEach(() => {
  installIndexedDbMock();
  sessionStorage.clear();
});

afterEach(() => {
  window.history.pushState({}, '', '/');
  sessionStorage.clear();
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
  cleanup();
});

describe('E2E — intersection modules serveur poste partagé (story 27.7)', () => {
  it('lock actif : GET effective-modules non appelé avant session opérateur', async () => {
    await saveDeviceIdentity({ device_id: deviceId, device_secret: 'sec-e2e-27-7' });
    const fetchMock = createLiveAuthFetchMock();
    vi.stubGlobal('fetch', fetchMock);

    renderLiveAuthApp();

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-lock-screen')).toBeTruthy();
    });

    const effectiveCalls = fetchMock.mock.calls.filter((c) =>
      String(c[0]).includes('/effective-modules'),
    );
    expect(effectiveCalls).toHaveLength(0);
  });

  it('post-PIN : fetch effective-modules avec cache no-store et en-têtes device', async () => {
    await saveDeviceIdentity({ device_id: deviceId, device_secret: 'sec-e2e-27-7' });
    const fetchMock = createLiveAuthFetchMock({ effectiveModules: 'with-banner' });
    vi.stubGlobal('fetch', fetchMock);

    renderLiveAuthApp();
    await unlockWithPin(fetchMock);

    const effectiveCall = fetchMock.mock.calls.find((c) =>
      String(c[0]).includes('/effective-modules'),
    );
    expect(effectiveCall).toBeTruthy();
    const init = effectiveCall![1] as RequestInit | undefined;
    expect(init?.cache).toBe('no-store');
    const headers = init?.headers as Record<string, string> | undefined;
    expect(headers?.Authorization).toMatch(/^Bearer /);
    expect(headers?.['X-Recyclique-Device-Id']).toBeTruthy();
  });

  it('post-PIN : shell navigation visible après modules effectifs chargés', async () => {
    await saveDeviceIdentity({ device_id: deviceId, device_secret: 'sec-e2e-27-7' });
    const fetchMock = createLiveAuthFetchMock({ effectiveModules: 'with-banner' });
    vi.stubGlobal('fetch', fetchMock);

    renderLiveAuthApp();
    await unlockWithPin(fetchMock);

    expect(await screen.findByRole('navigation', { name: 'Zone navigation' })).toBeTruthy();
    expect(await screen.findByTestId('shell-zone-main')).toBeTruthy();
  });

  it('effective-modules vide : shell reste accessible (projection serveur, pas crash UI)', async () => {
    await saveDeviceIdentity({ device_id: deviceId, device_secret: 'sec-e2e-27-7' });
    const fetchMock = createLiveAuthFetchMock({ effectiveModules: 'empty' });
    vi.stubGlobal('fetch', fetchMock);

    renderLiveAuthApp();
    await unlockWithPin(fetchMock);

    expect(await screen.findByRole('navigation', { name: 'Zone navigation' })).toBeTruthy();
    expect(screen.queryByTestId('shared-workstation-lock-screen')).toBeNull();
  });

  it('admin sans identité poste : pas de lock ni fetch effective-modules', async () => {
    const fetchMock = createLiveAuthFetchMock();
    vi.stubGlobal('fetch', fetchMock);

    renderLiveAuthApp();

    await waitFor(() => {
      expect(screen.queryByTestId('shared-workstation-lock-screen')).toBeNull();
    });
    await waitFor(() => {
      expect(screen.getByTestId('shell-zone-main')).toBeTruthy();
    });

    const effectiveCalls = fetchMock.mock.calls.filter((c) =>
      String(c[0]).includes('/effective-modules'),
    );
    expect(effectiveCalls).toHaveLength(0);
    expect(await hasDeviceIdentity()).toBe(false);
  });
});
