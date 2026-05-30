// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from '../../src/app/App';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { KPI_LIVE_BANNER_MODULE_KEY } from '../../src/api/module-config-client';
import {
  hasDeviceIdentity,
  loadDeviceIdentity,
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

function buildContextEnvelopeBody() {
  return {
    runtime_state: 'ok',
    permission_keys: [
      'transverse.dashboard.view',
      'transverse.admin.view',
      'recyclique.exploitation.view-live-band',
    ],
    computed_at: new Date().toISOString(),
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
}

type VerifyMode = 'success' | 'invalid' | 'locked';

function createLiveAuthFetchMock(options: { verifyMode?: VerifyMode } = {}) {
  let operatorSessionActive = false;
  const verifyMode = options.verifyMode ?? 'success';

  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const method = (init?.method ?? 'GET').toUpperCase();

    if (url.includes('/v1/users/me/context') && (method === 'GET' || method === 'POST')) {
      return new Response(JSON.stringify(buildContextEnvelopeBody()), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    if (url.includes('/shared-workstation/effective-modules') && method === 'GET') {
      if (!operatorSessionActive) {
        return new Response(
          JSON.stringify({
            code: 'SHARED_WORKSTATION_OPERATOR_REQUIRED',
            message: 'Session opérateur requise',
          }),
          { status: 403, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response(
        JSON.stringify({
          module_keys: ['kpi-live-banner', 'reception'],
          computed_at: new Date().toISOString(),
          site_id: siteId,
          device_id: deviceId,
          operator_user_id: operatorUserId,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    }

    if (url.includes('/shared-workstation/operator-session/status') && method === 'GET') {
      return new Response(
        JSON.stringify({
          active: operatorSessionActive,
          operator_user_id: operatorSessionActive ? operatorUserId : null,
          session_id: operatorSessionActive ? 'sess-e2e-27-6' : null,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    }

    if (url.includes('/shared-workstation/operator-pin/verify') && method === 'POST') {
      if (verifyMode === 'locked') {
        return new Response(
          JSON.stringify({
            code: 'SHARED_WORKSTATION_PIN_LOCKED',
            message: 'Trop de tentatives',
          }),
          { status: 429, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (verifyMode === 'invalid') {
        return new Response(
          JSON.stringify({
            code: 'SHARED_WORKSTATION_PIN_INVALID',
            message: 'Refus neutre',
          }),
          { status: 403, headers: { 'Content-Type': 'application/json' } },
        );
      }
      operatorSessionActive = true;
      return new Response(
        JSON.stringify({
          session_id: 'sess-e2e-27-6',
          device_id: deviceId,
          operator_user_id: operatorUserId,
          site_id: siteId,
          started_at: '2026-05-30T12:00:00Z',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    }

    if (url.includes('/shared-workstation/enroll/complete') && method === 'POST') {
      return new Response(
        JSON.stringify({
          device_id: deviceId,
          device_secret: 'sec-e2e-pin-lock',
          device_name: 'Poste Hall',
          site_id: siteId,
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
  sessionStorage.setItem(LIVE_AUTH_ACCESS_TOKEN_STORAGE_KEY, 'e2e-live-auth-token');
  window.history.pushState({}, '', '/dashboard');
  return render(
    <RootProviders>
      <App />
    </RootProviders>,
  );
}

function fillOperatorPinForm(pin = '1234') {
  fireEvent.change(screen.getByTestId('shared-workstation-operator-id'), {
    target: { value: operatorUserId },
  });
  const pinRoot = screen.getByTestId('shared-workstation-pin-input');
  const inputs = pinRoot.querySelectorAll('input');
  pin.split('').forEach((digit, i) => {
    fireEvent.change(inputs[i]!, { target: { value: digit } });
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

describe('E2E — lock screen PIN poste partagé (story 27.6)', () => {
  it('poste enrôlé + session JWT : lock screen masque le shell métier sans opérateur actif', async () => {
    await saveDeviceIdentity({ device_id: deviceId, device_secret: 'sec-e2e' });
    vi.stubGlobal('fetch', createLiveAuthFetchMock());

    renderLiveAuthApp();

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-lock-screen')).toBeTruthy();
    });
    expect(screen.queryByRole('navigation', { name: 'Zone navigation' })).toBeNull();
    expect(screen.queryByTestId('shell-zone-main')).toBeNull();
  });

  it('déverrouillage PIN nominal : shell navigation visible après succès API', async () => {
    await saveDeviceIdentity({ device_id: deviceId, device_secret: 'sec-e2e' });
    const fetchMock = createLiveAuthFetchMock({ verifyMode: 'success' });
    vi.stubGlobal('fetch', fetchMock);

    renderLiveAuthApp();

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-lock-screen')).toBeTruthy();
    });

    fillOperatorPinForm('4242');
    fireEvent.click(screen.getByTestId('shared-workstation-pin-submit'));

    await waitFor(() => {
      expect(screen.queryByTestId('shared-workstation-lock-screen')).toBeNull();
    });
    expect(await screen.findByRole('navigation', { name: 'Zone navigation' })).toBeTruthy();
    expect(fetchMock.mock.calls.some((c) => String(c[0]).includes('/operator-pin/verify'))).toBe(
      true,
    );
  });

  it('PIN invalide : message neutre, shell toujours masqué', async () => {
    await saveDeviceIdentity({ device_id: deviceId, device_secret: 'sec-e2e' });
    vi.stubGlobal('fetch', createLiveAuthFetchMock({ verifyMode: 'invalid' }));

    renderLiveAuthApp();

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-lock-screen')).toBeTruthy();
    });

    fillOperatorPinForm('0000');
    fireEvent.click(screen.getByTestId('shared-workstation-pin-submit'));

    await waitFor(() => {
      expect(screen.getByText(/Identifiant ou PIN incorrect/i)).toBeTruthy();
    });
    expect(screen.getByTestId('shared-workstation-lock-screen')).toBeTruthy();
    expect(screen.queryByRole('navigation', { name: 'Zone navigation' })).toBeNull();
  });

  it('lockout 429 : message trop de tentatives et saisie désactivée', async () => {
    await saveDeviceIdentity({ device_id: deviceId, device_secret: 'sec-e2e' });
    vi.stubGlobal('fetch', createLiveAuthFetchMock({ verifyMode: 'locked' }));

    renderLiveAuthApp();

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-lock-screen')).toBeTruthy();
    });

    fillOperatorPinForm('4242');
    fireEvent.click(screen.getByTestId('shared-workstation-pin-submit'));

    await waitFor(() => {
      expect(screen.getByText(/Trop de tentatives/i)).toBeTruthy();
    });
    expect(screen.getByTestId('shared-workstation-operator-id')).toHaveProperty('disabled', true);
    expect(screen.getByTestId('shared-workstation-pin-submit')).toHaveProperty('disabled', true);
  });

  it('parcours enrôlement puis lock : code → identité IndexedDB → lock au dashboard live', async () => {
    vi.stubGlobal('fetch', createLiveAuthFetchMock());

    window.history.pushState({}, '', '/shared-workstation/enroll');
    render(
      <RootProviders>
        <App />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-enrollment-code')).toBeTruthy();
    });

    fireEvent.change(screen.getByTestId('shared-workstation-enrollment-code'), {
      target: { value: 'ABCD2345' },
    });
    fireEvent.click(screen.getByTestId('shared-workstation-enrollment-submit'));

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-enrollment-success')).toBeTruthy();
    });
    expect(await hasDeviceIdentity()).toBe(true);
    const identity = await loadDeviceIdentity();
    expect(identity?.device_id).toBe(deviceId);

    cleanup();
    vi.unstubAllEnvs();

    vi.stubEnv('VITE_LIVE_AUTH', 'true');
    sessionStorage.setItem(LIVE_AUTH_ACCESS_TOKEN_STORAGE_KEY, 'e2e-post-enroll');
    window.history.pushState({}, '', '/dashboard');

    render(
      <RootProviders>
        <App />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-lock-screen')).toBeTruthy();
    });
    expect(screen.queryByTestId('shell-zone-main')).toBeNull();

    fillOperatorPinForm('4242');
    fireEvent.click(screen.getByTestId('shared-workstation-pin-submit'));

    await waitFor(() => {
      expect(screen.queryByTestId('shared-workstation-lock-screen')).toBeNull();
    });
    const main = await screen.findByTestId('shell-zone-main');
    expect(within(main).queryByTestId('page-access-blocked')).toBeNull();
  });
});
