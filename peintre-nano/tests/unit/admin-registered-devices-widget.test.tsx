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

function makeAuthStub(permissionKeys: string[]): AuthContextPort {
  return {
    getSession: () => ({ authenticated: true, userId: 'u1', userDisplayLabel: 'Test' }),
    getContextEnvelope: () => ({
      schemaVersion: '1',
      siteId,
      activeRegisterId: null,
      permissions: { permissionKeys },
      issuedAt: Date.now(),
      runtimeStatus: 'ok',
    }),
    getAccessToken: () => 'tok',
  };
}

const superAdminAuth = makeAuthStub(['transverse.admin.view', 'caisse.sale_correct']);
const siteAdminAuth = makeAuthStub(['transverse.admin.view']);

function okJson(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

const sampleDevice = {
  device_id: deviceId,
  device_type: 'shared_workstation',
  name: 'Poste Hall',
  site_id: siteId,
  status: 'pending_enrollment',
  allowed_module_keys: [KPI_LIVE_BANNER_MODULE_KEY],
  inactivity_timeout_seconds: null,
  last_contact_at: null,
};

function wrap(ui: ReactElement, auth: AuthContextPort) {
  return <RootProviders authAdapter={auth}>{ui}</RootProviders>;
}

describe('AdminRegisteredDevicesWidget', () => {
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

  it('garde non-super-admin : pas de fetch liste', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/module-config/')) {
        return okJson({
          schema_version: 1,
          payload: {},
          version: 0,
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminRegisteredDevicesWidget />, siteAdminAuth));

    expect(screen.getByText(/Réservé au super-admin/i)).toBeTruthy();
    await new Promise((r) => setTimeout(r, 50));
    const registeredCalls = fetchMock.mock.calls.filter((c) =>
      String(c[0]).includes('/v1/registered-devices'),
    );
    expect(registeredCalls).toHaveLength(0);
  });

  it('affiche la liste mockée pour super-admin', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/v1/registered-devices/') && (!init?.method || init.method === 'GET')) {
        return okJson([sampleDevice]);
      }
      if (url.includes('/v1/sites/') && (!init?.method || init.method === 'GET')) {
        return okJson([
          {
            id: siteId,
            name: 'Site Test',
            is_active: true,
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
        ]);
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminRegisteredDevicesWidget />, superAdminAuth));

    await waitFor(() => {
      expect(screen.getByText('Poste Hall')).toBeTruthy();
    });
    expect(screen.getByText(deviceId)).toBeTruthy();
  });

  it('modal create appelle POST registered-devices', async () => {
    let created = false;
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/v1/registered-devices/') && init?.method === 'POST') {
        created = true;
        const body = JSON.parse(String(init.body)) as Record<string, unknown>;
        expect(body.device_type).toBe('shared_workstation');
        return okJson({ ...sampleDevice, name: String(body.name) }, 201);
      }
      if (url.includes('/v1/registered-devices/') && (!init?.method || init.method === 'GET')) {
        return okJson(created ? [{ ...sampleDevice, name: 'Nouveau' }] : []);
      }
      if (url.includes('/v1/sites/')) {
        return okJson([
          {
            id: siteId,
            name: 'Site Test',
            is_active: true,
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
        ]);
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminRegisteredDevicesWidget />, superAdminAuth));

    await waitFor(() => {
      expect(fetchMock.mock.calls.some((c) => String(c[0]).includes('/v1/sites/'))).toBe(true);
    });

    fireEvent.click(screen.getByTestId('admin-registered-devices-create'));
    const dialog = await screen.findByRole('dialog');
    const modal = within(dialog);
    fireEvent.change(modal.getByTestId('admin-registered-devices-create-name'), {
      target: { value: 'Nouveau' },
    });
    await waitFor(() => {
      const btn = modal.getByTestId('admin-registered-devices-create-submit');
      expect(btn.hasAttribute('disabled')).toBe(false);
    });
    fireEvent.click(modal.getByTestId('admin-registered-devices-create-submit'));

    await waitFor(() => {
      expect(created).toBe(true);
    });
  });

  it('modal edit appelle PATCH registered-devices', async () => {
    let patched = false;
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (
        url.includes(`/v1/registered-devices/${deviceId}`) &&
        init?.method === 'PATCH'
      ) {
        patched = true;
        const body = JSON.parse(String(init.body)) as Record<string, unknown>;
        expect(body.name).toBe('Poste Renommé');
        return okJson({ ...sampleDevice, name: String(body.name) });
      }
      if (url.includes('/v1/registered-devices/') && (!init?.method || init.method === 'GET')) {
        return okJson([sampleDevice]);
      }
      if (url.includes('/v1/sites/')) {
        return okJson([
          {
            id: siteId,
            name: 'Site Test',
            is_active: true,
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
        ]);
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminRegisteredDevicesWidget />, superAdminAuth));

    await waitFor(() => {
      expect(screen.getByText('Poste Hall')).toBeTruthy();
    });

    fireEvent.click(screen.getByRole('button', { name: 'Modifier' }));
    const dialog = await screen.findByRole('dialog');
    const modal = within(dialog);
    const nameInput = await waitFor(() => {
      const input = modal.getByTestId('admin-registered-devices-edit-name');
      expect((input as HTMLInputElement).value).toBe('Poste Hall');
      return input;
    });
    fireEvent.change(nameInput, {
      target: { value: 'Poste Renommé' },
    });
    fireEvent.click(modal.getByTestId('admin-registered-devices-edit-submit'));

    await waitFor(() => {
      expect(patched).toBe(true);
    });
  });

  it('révocation appelle POST revoke', async () => {
    let revoked = false;
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/revoke') && init?.method === 'POST') {
        revoked = true;
        return okJson({ ...sampleDevice, status: 'revoked' });
      }
      if (url.includes('/v1/registered-devices/') && (!init?.method || init.method === 'GET')) {
        return okJson([sampleDevice]);
      }
      if (url.includes('/v1/sites/')) {
        return okJson([
          {
            id: siteId,
            name: 'Site Test',
            is_active: true,
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
        ]);
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminRegisteredDevicesWidget />, superAdminAuth));

    await waitFor(() => {
      expect(screen.getByText('Poste Hall')).toBeTruthy();
    });

    const revokeButtons = screen.getAllByTestId('admin-registered-devices-revoke');
    fireEvent.click(revokeButtons[0]);
    await waitFor(() => {
      expect(screen.getByTestId('admin-registered-devices-revoke-confirm')).toBeTruthy();
    });
    fireEvent.click(screen.getByTestId('admin-registered-devices-revoke-confirm'));

    await waitFor(() => {
      expect(revoked).toBe(true);
    });
  });
});
