// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import type { ReactElement } from 'react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import type { AuthContextPort } from '../../src/app/auth/auth-context-port';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { AdminModulesWidget } from '../../src/domains/admin-config/AdminModulesWidget';
import {
  KPI_LIVE_BANNER_MODULE_KEY,
  KPI_LIVE_BANNER_SCHEMA_VERSION,
} from '../../src/api/module-config-client';
import {
  COMPTAGE_PIECES_BILLETS_MODULE_KEY,
} from '../../src/api/comptage-module-config';
import '../../src/styles/tokens.css';

const siteId = '550e8400-e29b-41d4-a716-446655440000';

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

const superAdminAuthStub: AuthContextPort = makeAuthStub(['transverse.admin.view', 'caisse.sale_correct']);
const siteAdminAuthStub: AuthContextPort = makeAuthStub(['transverse.admin.view']);

const authStub: AuthContextPort = superAdminAuthStub;

const defaultDoc = {
  schema_version: KPI_LIVE_BANNER_SCHEMA_VERSION,
  payload: {
    show_on_caisse: true,
    show_on_reception: true,
    refresh_interval_seconds: 60,
  },
  version: 0,
};

function okJson(body: unknown, status = 200, etag?: string): Response {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (etag) headers.ETag = etag;
  return new Response(JSON.stringify(body), { status, headers });
}

function moduleConfigUrl(): string {
  return `/v1/sites/${siteId}/module-config/${KPI_LIVE_BANNER_MODULE_KEY}`;
}

function wrap(ui: ReactElement) {
  return <RootProviders authAdapter={authStub}>{ui}</RootProviders>;
}

describe('AdminModulesWidget', () => {
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

  it('charge GET module-config et enregistre via PATCH avec If-Match', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes(moduleConfigUrl()) && (!init?.method || init.method === 'GET')) {
        return okJson(defaultDoc, 200, 'W/"0"');
      }
      if (url.includes(moduleConfigUrl()) && init?.method === 'PATCH') {
        expect(init.headers).toMatchObject({ 'If-Match': 'W/"0"' });
        const body = JSON.parse(String(init.body)) as typeof defaultDoc;
        expect(body.payload.show_on_caisse).toBe(false);
        return okJson(
          {
            ...defaultDoc,
            payload: { ...defaultDoc.payload, show_on_caisse: false },
            version: 1,
          },
          200,
          'W/"1"',
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminModulesWidget />));

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-server-source')).toBeTruthy();
    });

    const caisseSwitch = screen.getByTestId('admin-kpi-live-toggle-caisse');
    fireEvent.click(caisseSwitch);

    fireEvent.change(screen.getByTestId('admin-modules-patch-motif'), {
      target: { value: 'Test inventaire' },
    });

    fireEvent.click(screen.getByTestId('admin-modules-save'));

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-save-success')).toBeTruthy();
    });

    expect(fetchMock.mock.calls.some((c) => String(c[0]).includes(moduleConfigUrl()))).toBe(true);
    const patchCall = fetchMock.mock.calls.find(
      (c) => String(c[0]).includes(moduleConfigUrl()) && (c[1] as RequestInit)?.method === 'PATCH',
    );
    expect(patchCall).toBeTruthy();
  });

  it('autorise un administrateur de site quand transverse.admin.view est présent', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes(moduleConfigUrl()) && (!init?.method || init.method === 'GET')) {
        return okJson(defaultDoc, 200, 'W/"0"');
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);
    render(
      <RootProviders authAdapter={siteAdminAuthStub}>
        <AdminModulesWidget />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-widget')).toBeTruthy();
    });
    expect(screen.queryByTestId('admin-modules-denied')).toBeNull();
  });

  it('désactive l’enregistrement et n’envoie aucun PATCH si le GET initial échoue', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes(moduleConfigUrl()) && (!init?.method || init.method === 'GET')) {
        return new Response(
          JSON.stringify({ detail: 'Erreur serveur module-config.' }),
          { status: 503, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.includes(moduleConfigUrl()) && init?.method === 'PATCH') {
        throw new Error('PATCH ne doit pas être appelé après un GET en échec');
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminModulesWidget />));

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-save-error')).toBeTruthy();
    });

    fireEvent.click(screen.getByTestId('admin-kpi-live-toggle-caisse'));
    expect((screen.getByTestId('admin-modules-save') as HTMLButtonElement).disabled).toBe(true);
    expect(fetchMock.mock.calls.some((c) => (c[1] as RequestInit | undefined)?.method === 'PATCH')).toBe(false);
  });

  it('refuse l’accès sans transverse.admin.view', () => {
    const limitedAuth: AuthContextPort = makeAuthStub([]);
    render(
      <RootProviders authAdapter={limitedAuth}>
        <AdminModulesWidget />
      </RootProviders>,
    );
    expect(screen.getByTestId('admin-modules-denied')).toBeTruthy();
  });

  it('affiche la carte comptage pièces/billets dans le catalogue', async () => {
    const comptageDefault = {
      schema_version: '1.0.0',
      payload: {
        enabled: false,
        skip_allowed: true,
        require_denomination_grid: false,
        show_images: true,
      },
      version: 0,
    };
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes(moduleConfigUrl()) && (!init?.method || init.method === 'GET')) {
        return okJson(defaultDoc, 200, 'W/"0"');
      }
      if (url.includes(`/module-config/${COMPTAGE_PIECES_BILLETS_MODULE_KEY}`) && (!init?.method || init.method === 'GET')) {
        return okJson(comptageDefault, 200, 'W/"0"');
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminModulesWidget />));

    await waitFor(() => {
      expect(screen.getByTestId(`admin-modules-accordion-${COMPTAGE_PIECES_BILLETS_MODULE_KEY}`)).toBeTruthy();
    });
    expect(screen.getByText('Comptage pièces / billets (clôture)')).toBeTruthy();
  });

  it('enregistre comptage via PATCH avec If-Match', async () => {
    const comptageDefault = {
      schema_version: '1.0.0',
      payload: {
        enabled: false,
        skip_allowed: true,
        require_denomination_grid: false,
        show_images: true,
      },
      version: 0,
    };
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes(moduleConfigUrl()) && (!init?.method || init.method === 'GET')) {
        return okJson(defaultDoc, 200, 'W/"0"');
      }
      if (url.includes(`/module-config/${COMPTAGE_PIECES_BILLETS_MODULE_KEY}`) && (!init?.method || init.method === 'GET')) {
        return okJson(comptageDefault, 200, 'W/"0"');
      }
      if (url.includes(`/module-config/${COMPTAGE_PIECES_BILLETS_MODULE_KEY}`) && init?.method === 'PATCH') {
        expect(init.headers).toMatchObject({ 'If-Match': 'W/"0"' });
        const body = JSON.parse(String(init.body)) as typeof comptageDefault;
        expect(body.payload.enabled).toBe(true);
        return okJson(
          {
            ...comptageDefault,
            payload: { ...comptageDefault.payload, enabled: true },
            version: 1,
          },
          200,
          'W/"1"',
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminModulesWidget />));

    await waitFor(() => {
      expect(screen.getByTestId('comptage-pieces-billets-module-panel')).toBeTruthy();
    });

    fireEvent.click(screen.getByTestId('admin-comptage-toggle-enabled'));
    fireEvent.click(screen.getByTestId('admin-comptage-save'));

    await waitFor(() => {
      expect(screen.getByTestId('admin-comptage-save-success')).toBeTruthy();
    });
  });
});
