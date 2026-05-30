// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from '../../src/app/App';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { KPI_LIVE_BANNER_MODULE_KEY } from '../../src/api/module-config-client';
import {
  clearDeviceIdentity,
  hasDeviceIdentity,
  loadDeviceIdentity,
  saveDeviceIdentity,
} from '../../src/domains/shared-workstation/device-identity-store';
import '../../src/registry';
import '../../src/styles/tokens.css';

const siteId = '550e8400-e29b-41d4-a716-446655440000';
const deviceId = '660e8400-e29b-41d4-a716-446655440001';

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

function renderApp() {
  return render(
    <RootProviders>
      <App />
    </RootProviders>,
  );
}

const samplePendingDevice = {
  device_id: deviceId,
  device_type: 'shared_workstation',
  name: 'Poste Hall',
  site_id: siteId,
  status: 'pending_enrollment',
  allowed_module_keys: [KPI_LIVE_BANNER_MODULE_KEY],
  inactivity_timeout_seconds: null,
  last_contact_at: null,
};

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
});

afterEach(() => {
  window.history.pushState({}, '', '/');
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  cleanup();
});

describe('E2E — enrôlement poste partagé (story 27.4)', () => {
  it('URL profonde /shared-workstation/enroll : widget public sans blocage accès', async () => {
    window.history.pushState({}, '', '/shared-workstation/enroll');
    renderApp();

    const main = screen.getByTestId('shell-zone-main');
    expect(within(main).queryByTestId('page-access-blocked')).toBeNull();
    await waitFor(() => {
      expect(within(main).getByTestId('shared-workstation-enrollment')).toBeTruthy();
    });
    expect(
      within(main).getByRole('heading', {
        level: 2,
        name: /Enrôlement du poste/i,
      }),
    ).toBeTruthy();
    expect(within(main).getByTestId('shared-workstation-enrollment-code')).toBeTruthy();
    expect(within(main).getByTestId('shared-workstation-enrollment-submit')).toBeTruthy();
  });

  it('premier enrôlement : pas de bannière identité perdue', async () => {
    window.history.pushState({}, '', '/shared-workstation/enroll');
    renderApp();

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-enrollment')).toBeTruthy();
    });
    expect(screen.queryByTestId('shared-workstation-identity-lost-banner')).toBeNull();
  });

  it('identité perdue réelle : bannière reconnexion (hint sans credential)', async () => {
    await saveDeviceIdentity({ device_id: deviceId, device_secret: 'was-here' });
    await clearDeviceIdentity();

    window.history.pushState({}, '', '/shared-workstation/enroll');
    renderApp();

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-identity-lost-banner')).toBeTruthy();
    });
  });

  it('chemin nominal : saisie code → API complete → identité IndexedDB', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/shared-workstation/enroll/complete') && method === 'POST') {
        return new Response(
          JSON.stringify({
            device_id: deviceId,
            device_secret: 'sec-e2e-test',
            device_name: 'Poste Hall',
            site_id: siteId,
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } });
    });
    vi.stubGlobal('fetch', fetchMock);

    window.history.pushState({}, '', '/shared-workstation/enroll');
    renderApp();

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

    expect(fetchMock.mock.calls.some((c) => String(c[0]).includes('/enroll/complete'))).toBe(true);
    expect(await hasDeviceIdentity()).toBe(true);
    const identity = await loadDeviceIdentity();
    expect(identity?.device_id).toBe(deviceId);
    expect(identity?.device_secret).toBe('sec-e2e-test');
  });

  it('code expiré : erreur visible dans le formulaire (ENROLLMENT_CODE_EXPIRED)', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/shared-workstation/enroll/complete') && method === 'POST') {
        return new Response(
          JSON.stringify({
            detail: { code: 'ENROLLMENT_CODE_EXPIRED', message: 'Code expiré' },
          }),
          { status: 410, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } });
    });
    vi.stubGlobal('fetch', fetchMock);

    window.history.pushState({}, '', '/shared-workstation/enroll');
    renderApp();

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-enrollment-code')).toBeTruthy();
    });

    fireEvent.change(screen.getByTestId('shared-workstation-enrollment-code'), {
      target: { value: 'EXPIRED1' },
    });
    fireEvent.click(screen.getByTestId('shared-workstation-enrollment-submit'));

    const form = screen.getByTestId('shared-workstation-enrollment');
    await waitFor(() => {
      expect(within(form).getByText(/expiré|ENROLLMENT_CODE_EXPIRED/i)).toBeTruthy();
    });
    expect(await hasDeviceIdentity()).toBe(false);
  });

  it('panel SuperAdmin : URL /admin/registered-devices → génération code enrôlement', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/registered-devices') && method === 'GET' && !url.includes('/enrollment-codes')) {
        return new Response(JSON.stringify([samplePendingDevice]), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/sites') && method === 'GET') {
        return new Response(JSON.stringify([{ id: siteId, name: 'Site A', is_active: true }]), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/enrollment-codes') && method === 'POST') {
        return new Response(
          JSON.stringify({
            code: 'ABCD2345',
            expires_at: new Date(Date.now() + 900_000).toISOString(),
            purpose: 'initial_enrollment',
          }),
          { status: 201, headers: { 'Content-Type': 'application/json' } },
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
    vi.stubGlobal('fetch', fetchMock);

    window.history.pushState({}, '', '/admin/registered-devices');
    renderApp();

    const main = screen.getByTestId('shell-zone-main');
    await waitFor(() => {
      expect(within(main).getByTestId('widget-admin-registered-devices')).toBeTruthy();
    });
    await waitFor(() => {
      expect(within(main).getByTestId('admin-registered-devices-issue-enrollment-code')).toBeTruthy();
    });

    fireEvent.click(within(main).getByTestId('admin-registered-devices-issue-enrollment-code'));

    const codeDisplay = await screen.findByTestId('admin-registered-devices-code-display');
    expect(codeDisplay.textContent).toBe('ABCD2345');
    expect(fetchMock.mock.calls.some((c) => String(c[0]).includes('/enrollment-codes'))).toBe(true);
  });

  it('panel SuperAdmin : boutons reconnect / replace / conflit selon statut device', async () => {
    const devices = [
      { ...samplePendingDevice, device_id: 'd1', status: 'identity_lost', name: 'Perdu' },
      { ...samplePendingDevice, device_id: 'd2', status: 'active', name: 'Actif' },
      { ...samplePendingDevice, device_id: 'd3', status: 'conflict', name: 'Conflit' },
    ];
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/registered-devices') && method === 'GET' && !url.includes('/enrollment-codes')) {
        return new Response(JSON.stringify(devices), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/sites') && method === 'GET') {
        return new Response(JSON.stringify([{ id: siteId, name: 'Site A', is_active: true }]), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/module-config/') && method === 'GET') {
        return new Response(
          JSON.stringify({ schema_version: 1, payload: {}, version: 0 }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } });
    });
    vi.stubGlobal('fetch', fetchMock);

    window.history.pushState({}, '', '/admin/registered-devices');
    renderApp();

    const main = screen.getByTestId('shell-zone-main');
    await waitFor(() => {
      expect(within(main).getByTestId('admin-registered-devices-reconnect-code')).toBeTruthy();
    });
    expect(within(main).getByTestId('admin-registered-devices-replace-code')).toBeTruthy();
    expect(within(main).getByTestId('admin-registered-devices-resolve-conflict')).toBeTruthy();
    expect(within(main).queryByTestId('admin-registered-devices-issue-enrollment-code')).toBeNull();
  });

  it('panel SuperAdmin : replace_definitively ouvre modal code replace auto', async () => {
    const conflictDevice = {
      ...samplePendingDevice,
      status: 'conflict',
      name: 'Conflit E2E',
    };
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/registered-devices') && method === 'GET' && !url.includes('/enrollment-codes')) {
        return new Response(JSON.stringify([conflictDevice]), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/sites') && method === 'GET') {
        return new Response(JSON.stringify([{ id: siteId, name: 'Site A', is_active: true }]), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/resolve-conflict') && method === 'POST') {
        const body = JSON.parse(String(init?.body ?? '{}')) as { action?: string };
        expect(body.action).toBe('replace_definitively');
        return new Response(
          JSON.stringify({
            status: 'active',
            device_id: deviceId,
            enrollment_code: 'REPL5678',
            enrollment_code_expires_at: new Date(Date.now() + 900_000).toISOString(),
            enrollment_code_purpose: 'replace',
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
    vi.stubGlobal('fetch', fetchMock);

    window.history.pushState({}, '', '/admin/registered-devices');
    renderApp();

    const main = screen.getByTestId('shell-zone-main');
    await waitFor(() => {
      expect(within(main).getByTestId('admin-registered-devices-resolve-conflict')).toBeTruthy();
    });
    fireEvent.click(within(main).getByTestId('admin-registered-devices-resolve-conflict'));
    await waitFor(() => {
      expect(screen.getByText(/Résoudre le conflit d'identité/)).toBeTruthy();
    });
    fireEvent.click(screen.getByRole('button', { name: /Remplacer définitivement/i }));

    const codeDisplay = await screen.findByTestId('admin-registered-devices-code-display');
    expect(codeDisplay.textContent).toBe('REPL5678');
    expect(fetchMock.mock.calls.some((c) => String(c[0]).includes('/resolve-conflict'))).toBe(true);
  });

  it('identité existante : pas de bannière perdue au montage', async () => {
    await saveDeviceIdentity({ device_id: deviceId, device_secret: 'existing' });
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } })),
    );

    window.history.pushState({}, '', '/shared-workstation/enroll');
    renderApp();

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-enrollment')).toBeTruthy();
    });
    expect(screen.queryByTestId('shared-workstation-identity-lost-banner')).toBeNull();
    await clearDeviceIdentity();
  });
});
