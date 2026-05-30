// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import type { ReactElement } from 'react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import type { AuthContextPort } from '../../src/app/auth/auth-context-port';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { AdminRegisteredDevicesWidget } from '../../src/domains/admin-config/AdminRegisteredDevicesWidget';
import { KPI_LIVE_BANNER_MODULE_KEY } from '../../src/api/module-config-client';
import '../../src/styles/tokens.css';

const siteId = '550e8400-e29b-41d4-a716-446655440000';
const deviceId = '660e8400-e29b-41d4-a716-446655440001';

function makeAuthStub(): AuthContextPort {
  return {
    getSession: () => ({ authenticated: true, userId: 'u1', userDisplayLabel: 'Test' }),
    getContextEnvelope: () => ({
      schemaVersion: '1',
      siteId,
      activeRegisterId: null,
      permissions: { permissionKeys: ['transverse.admin.view', 'caisse.sale_correct'] },
      issuedAt: Date.now(),
      runtimeStatus: 'ok',
    }),
    getAccessToken: () => 'tok',
  };
}

const sampleDevice = {
  device_id: deviceId,
  device_type: 'shared_workstation' as const,
  name: 'Poste Hall',
  site_id: siteId,
  status: 'pending_enrollment',
  allowed_module_keys: [KPI_LIVE_BANNER_MODULE_KEY],
};

function wrap(ui: ReactElement) {
  return <RootProviders authAdapter={makeAuthStub()}>{ui}</RootProviders>;
}

describe('AdminRegisteredDevicesWidget enrollment actions', () => {
  beforeAll(() => {
    globalThis.ResizeObserver = class {
      observe(): void {}
      unobserve(): void {}
      disconnect(): void {}
    } as typeof ResizeObserver;
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it('bouton code enrôlement appelle POST enrollment-codes', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? 'GET';
      if (url.includes('/registered-devices') && method === 'GET') {
        return new Response(JSON.stringify([sampleDevice]), {
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
            expires_at: new Date().toISOString(),
            purpose: 'initial_enrollment',
          }),
          { status: 201, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminRegisteredDevicesWidget widgetType="admin.registered-devices.demo" />));
    await waitFor(() => {
      expect(screen.getByTestId('admin-registered-devices-issue-enrollment-code')).toBeTruthy();
    });
    fireEvent.click(screen.getByTestId('admin-registered-devices-issue-enrollment-code'));
    await waitFor(() => {
      expect(screen.getByTestId('admin-registered-devices-code-display')).toBeTruthy();
    });
    const calls = fetchMock.mock.calls.map((c) => String(c[0]));
    expect(calls.some((u) => u.includes('/enrollment-codes'))).toBe(true);
  });

  it('bouton reconnecter appelle POST enrollment-codes purpose reconnect', async () => {
    const lostDevice = { ...sampleDevice, status: 'identity_lost' as const };
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? 'GET';
      if (url.includes('/registered-devices') && method === 'GET') {
        return new Response(JSON.stringify([lostDevice]), {
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
        const body = JSON.parse(String(init?.body ?? '{}')) as { purpose?: string };
        expect(body.purpose).toBe('reconnect');
        return new Response(
          JSON.stringify({
            code: 'RECN2345',
            expires_at: new Date().toISOString(),
            purpose: 'reconnect',
          }),
          { status: 201, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminRegisteredDevicesWidget widgetType="admin.registered-devices.demo" />));
    await waitFor(() => {
      expect(screen.getByTestId('admin-registered-devices-reconnect-code')).toBeTruthy();
    });
    fireEvent.click(screen.getByTestId('admin-registered-devices-reconnect-code'));
    await waitFor(() => {
      expect(screen.getByTestId('admin-registered-devices-code-display')).toBeTruthy();
    });
  });

  it('résoudre conflit refuse appelle POST resolve-conflict', async () => {
    const conflictDevice = { ...sampleDevice, status: 'conflict' as const };
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? 'GET';
      if (url.includes('/registered-devices') && method === 'GET') {
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
        expect(body.action).toBe('refuse');
        return new Response(
          JSON.stringify({ status: 'active', device_id: deviceId }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminRegisteredDevicesWidget widgetType="admin.registered-devices.demo" />));
    await waitFor(() => {
      expect(screen.getByTestId('admin-registered-devices-resolve-conflict')).toBeTruthy();
    });
    fireEvent.click(screen.getByTestId('admin-registered-devices-resolve-conflict'));
    await waitFor(() => {
      expect(screen.getByText(/Résoudre le conflit d'identité/)).toBeTruthy();
    });
    fireEvent.click(
      screen.getByRole('button', { name: /Refuser l'ancienne machine/ }),
    );
    await waitFor(() => {
      expect(fetchMock.mock.calls.some((c) => String(c[0]).includes('/resolve-conflict'))).toBe(true);
    });
  });

  it('résoudre replace_definitively affiche le code replace auto-émis', async () => {
    const conflictDevice = { ...sampleDevice, status: 'conflict' as const };
    const expiresAt = new Date(Date.now() + 900_000).toISOString();
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? 'GET';
      if (url.includes('/registered-devices') && method === 'GET') {
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
            enrollment_code: 'REPL2345',
            enrollment_code_expires_at: expiresAt,
            enrollment_code_purpose: 'replace',
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminRegisteredDevicesWidget widgetType="admin.registered-devices.demo" />));
    await waitFor(() => {
      expect(screen.getByTestId('admin-registered-devices-resolve-conflict')).toBeTruthy();
    });
    fireEvent.click(screen.getByTestId('admin-registered-devices-resolve-conflict'));
    await waitFor(() => {
      expect(screen.getByText(/Résoudre le conflit d'identité/)).toBeTruthy();
    });
    fireEvent.click(
      screen.getByRole('button', { name: /Remplacer définitivement/i }),
    );
    await waitFor(() => {
      expect(screen.getByTestId('admin-registered-devices-code-display')).toBeTruthy();
    });
    expect(screen.getByTestId('admin-registered-devices-code-display').textContent).toBe('REPL2345');
    expect(fetchMock.mock.calls.some((c) => String(c[0]).includes('/resolve-conflict'))).toBe(true);
  });
});
