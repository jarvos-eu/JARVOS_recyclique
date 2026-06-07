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
import { CONTEXT_ACTIVE_SITE_DISPLAY_NAME_KEY } from '../../src/runtime/context-presentation-keys';
import '../../src/styles/tokens.css';

const siteId = '550e8400-e29b-41d4-a716-446655440000';
const siteName = 'Recyclerie Pilote';

function makeAuthStub(overrides?: Partial<ReturnType<AuthContextPort['getContextEnvelope']>>): AuthContextPort {
  return {
    getSession: () => ({ authenticated: true, userId: 'u1', userDisplayLabel: 'Test' }),
    getContextEnvelope: () => ({
      schemaVersion: '1',
      siteId,
      activeRegisterId: null,
      permissions: { permissionKeys: ['transverse.admin.view', 'caisse.sale_correct'] },
      issuedAt: Date.now(),
      runtimeStatus: 'ok',
      ...overrides,
    }),
    getAccessToken: () => 'tok',
  };
}

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

function wrap(ui: ReactElement, auth: AuthContextPort = makeAuthStub()) {
  return <RootProviders authAdapter={auth}>{ui}</RootProviders>;
}

describe('AdminModulesWidget human copy 28-4', () => {
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

  it('affiche une copie planché sans jargon dev ni UUID brut', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/v1/sites') && !url.includes('/module-config') && (!init?.method || init.method === 'GET')) {
        return okJson([
          {
            id: siteId,
            name: siteName,
            is_active: true,
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
        ]);
      }
      if (url.includes(moduleConfigUrl()) && (!init?.method || init.method === 'GET')) {
        return okJson(defaultDoc, 200, 'W/"0"');
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminModulesWidget />));

    expect(screen.getByText(/Activez et réglez les modules pour le site courant/i)).toBeTruthy();
    expect(screen.queryByText(/module-config/i)).toBeNull();
    expect(screen.queryByText(/getLiveSnapshot/i)).toBeNull();

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-site-label').textContent).toBe(siteName);
    });
    expect(screen.queryByText(siteId)).toBeNull();
  });

  it('priorise presentationLabels pour le nom de site', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes(moduleConfigUrl()) && (!init?.method || init.method === 'GET')) {
        return okJson(defaultDoc, 200, 'W/"0"');
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const auth = makeAuthStub({
      presentationLabels: { [CONTEXT_ACTIVE_SITE_DISPLAY_NAME_KEY]: 'Site depuis enveloppe' },
    });
    render(wrap(<AdminModulesWidget />, auth));

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-site-label').textContent).toBe('Site depuis enveloppe');
    });
  });

  it('active l’enregistrement après GET 200 sans header ETag (repli version)', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes(moduleConfigUrl()) && (!init?.method || init.method === 'GET')) {
        return okJson(defaultDoc, 200);
      }
      if (url.includes(moduleConfigUrl()) && init?.method === 'PATCH') {
        expect(init.headers).toMatchObject({ 'If-Match': 'W/"0"' });
        return okJson({ ...defaultDoc, version: 1 }, 200, 'W/"1"');
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminModulesWidget />));

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-server-source')).toBeTruthy();
    });

    fireEvent.click(screen.getByTestId('admin-kpi-live-toggle-caisse'));
    fireEvent.click(screen.getByTestId('admin-modules-save'));

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-save-success')).toBeTruthy();
    });
  });

  it('affiche un UUID tronqué si ni presentationLabels ni liste sites', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/v1/sites') && !url.includes('/module-config') && (!init?.method || init.method === 'GET')) {
        return okJson([]);
      }
      if (url.includes(moduleConfigUrl()) && (!init?.method || init.method === 'GET')) {
        return okJson(defaultDoc, 200, 'W/"0"');
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminModulesWidget />));

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-site-label').textContent).toBe(`${siteId.slice(0, 8)}…`);
    });
    expect(screen.queryByText(siteId)).toBeNull();
  });

  it('affiche un message d’erreur FR lisible au chargement échoué', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes(moduleConfigUrl()) && (!init?.method || init.method === 'GET')) {
        return new Response(JSON.stringify({ detail: 'Erreur temporaire' }), {
          status: 503,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminModulesWidget />));

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-save-error')).toBeTruthy();
    });
    expect(
      screen.getByText(/Erreur temporaire.*Recharger la configuration/i),
    ).toBeTruthy();
  });

  it('affiche un message droits sur GET module-config 403', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes(moduleConfigUrl()) && (!init?.method || init.method === 'GET')) {
        return new Response(JSON.stringify({ detail: 'Accès refusé' }), {
          status: 403,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminModulesWidget />));

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-save-error')).toBeTruthy();
    });
    expect(
      screen.getByText(/Vous n’avez pas les droits pour lire la configuration des modules/i),
    ).toBeTruthy();
  });

  it('recharge la configuration via le bouton dédié', async () => {
    let getCount = 0;
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes(moduleConfigUrl()) && (!init?.method || init.method === 'GET')) {
        getCount += 1;
        if (getCount === 1) {
          return new Response(JSON.stringify({ detail: 'Erreur temporaire' }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' },
          });
        }
        return okJson(defaultDoc, 200, 'W/"0"');
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(wrap(<AdminModulesWidget />));

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-save-error')).toBeTruthy();
    });

    fireEvent.click(screen.getByTestId('admin-modules-reload-config'));

    await waitFor(() => {
      expect(screen.getByTestId('admin-modules-server-source')).toBeTruthy();
    });
    expect(getCount).toBeGreaterThanOrEqual(2);
  });
});
