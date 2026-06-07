// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { RuntimeDemoApp } from '../../src/app/demo/RuntimeDemoApp';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import {
  createDefaultDemoEnvelope,
  DEMO_AUTH_STUB_SITE_ID,
} from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import {
  KPI_LIVE_BANNER_MODULE_KEY,
  KPI_LIVE_BANNER_SCHEMA_VERSION,
} from '../../src/api/module-config-client';
import { COMPTAGE_PIECES_BILLETS_MODULE_KEY } from '../../src/api/comptage-module-config';
import { CONTEXT_ACTIVE_SITE_DISPLAY_NAME_KEY } from '../../src/runtime/context-presentation-keys';
import { comptageModuleDisabledJson } from '../unit/fixtures/cash-denominations-api';
import '../../src/registry';
import '../../src/styles/tokens.css';

const siteId = DEMO_AUTH_STUB_SITE_ID;
const siteName = 'Recyclerie Pilote E2E';

const kpiDefaultDoc = {
  schema_version: KPI_LIVE_BANNER_SCHEMA_VERSION,
  payload: {
    show_on_caisse: true,
    show_on_reception: true,
    refresh_interval_seconds: 60,
  },
  version: 0,
};

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

function okJson(body: unknown, status = 200, etag?: string): Response {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (etag) headers.ETag = etag;
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: {
      get: (k: string) => headers[k] ?? null,
    },
    text: async () => JSON.stringify(body),
    json: async () => body,
  } as Response;
}

function moduleConfigPath(moduleKey: string): string {
  return `/v1/sites/${siteId}/module-config/${moduleKey}`;
}

function buildModulesFetchMock(options?: {
  kpiEtag?: string | null;
  kpiGetFailsFirst?: boolean;
}) {
  let kpiGetCount = 0;
  const kpiEtag = options?.kpiEtag === undefined ? 'W/"0"' : options.kpiEtag;

  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = requestUrl(input);
    const method = (init?.method ?? 'GET').toUpperCase();

    if (url.includes('/v1/sites') && !url.includes('/module-config') && method === 'GET') {
      return Promise.resolve(
        okJson([
          {
            id: siteId,
            name: siteName,
            is_active: true,
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
        ]),
      );
    }

    if (url.includes(moduleConfigPath(KPI_LIVE_BANNER_MODULE_KEY)) && method === 'GET') {
      kpiGetCount += 1;
      if (options?.kpiGetFailsFirst && kpiGetCount === 1) {
        return Promise.resolve(
          okJson({ detail: 'Erreur temporaire' }, 503),
        );
      }
      if (kpiEtag) {
        return Promise.resolve(okJson(kpiDefaultDoc, 200, kpiEtag));
      }
      return Promise.resolve(okJson(kpiDefaultDoc, 200));
    }

    if (url.includes(moduleConfigPath(KPI_LIVE_BANNER_MODULE_KEY)) && method === 'PATCH') {
      expect(init?.headers).toMatchObject({ 'If-Match': 'W/"0"' });
      return Promise.resolve(okJson({ ...kpiDefaultDoc, version: 1 }, 200, 'W/"1"'));
    }

    if (url.includes(moduleConfigPath(COMPTAGE_PIECES_BILLETS_MODULE_KEY)) && method === 'GET') {
      return Promise.resolve(okJson(comptageModuleDisabledJson(), 200, 'W/"0"'));
    }

    if (url.includes('/v2/exploitation/live-snapshot') && method === 'GET') {
      return Promise.resolve(
        okJson({
          observed_at: '2026-06-07T12:00:00Z',
          effective_open_state: 'open',
        }),
      );
    }

    if (url.includes('/v1/stats/live') && method === 'GET') {
      return Promise.resolve(okJson({ tickets_open: 0 }));
    }

    return Promise.resolve(okJson({}));
  });
}

function renderAdminModulesRoute() {
  const auth = createMockAuthAdapter({
    session: { authenticated: true, userId: 'u-admin-modules-28-4-e2e' },
    envelope: createDefaultDemoEnvelope({
      presentationLabels: {
        [CONTEXT_ACTIVE_SITE_DISPLAY_NAME_KEY]: siteName,
      },
    }),
    accessToken: 'tok',
  });

  return render(
    <RootProviders authAdapter={auth} disableUserPrefsPersistence>
      <RuntimeDemoApp />
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

describe('E2E — Story 28.4 admin modules copie humaine (REV-ADMIN-02/03, REV-TRANSVERSE-04/05)', () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
    window.history.pushState({}, '', '/admin/modules');
  });

  afterEach(() => {
    window.history.pushState({}, '', '/');
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
    cleanup();
  });

  it('RuntimeDemoApp /admin/modules : copie planché, nom site lisible, sans jargon (AC-MODULES-COPY)', async () => {
    vi.stubEnv('VITE_LIVE_AUTH', 'true');
    vi.stubGlobal('fetch', buildModulesFetchMock());

    renderAdminModulesRoute();

    const main = await screen.findByTestId('shell-zone-main');
    await waitFor(() => {
      expect(within(main).getByTestId('admin-modules-widget')).toBeTruthy();
    });

    expect(within(main).getByText(/Activez et réglez les modules pour le site courant/i)).toBeTruthy();
    expect(within(main).queryByText(/module-config/i)).toBeNull();
    expect(within(main).queryByText(/getLiveSnapshot/i)).toBeNull();

    await waitFor(() => {
      expect(within(main).getByTestId('admin-modules-site-label').textContent).toBe(siteName);
    });
    expect(within(main).queryByText(siteId)).toBeNull();
  });

  it('parcours e2e : toggle KPI + enregistrement sans header ETag HTTP (AC-MODULES-SAVE-FIX)', async () => {
    vi.stubEnv('VITE_LIVE_AUTH', 'true');
    const fetchMock = buildModulesFetchMock({ kpiEtag: null });
    vi.stubGlobal('fetch', fetchMock);

    renderAdminModulesRoute();

    const main = await screen.findByTestId('shell-zone-main');
    await waitFor(() => {
      expect(within(main).getByTestId('admin-modules-server-source')).toBeTruthy();
    });

    fireEvent.click(within(main).getByTestId('admin-kpi-live-toggle-caisse'));
    fireEvent.click(within(main).getByTestId('admin-modules-save'));

    await waitFor(() => {
      expect(within(main).getByTestId('admin-modules-save-success')).toBeTruthy();
    });

    const patchCall = fetchMock.mock.calls.find(([inp, init]) => {
      const url = requestUrl(inp as RequestInfo);
      const method = (init?.method ?? 'GET').toUpperCase();
      return url.includes(moduleConfigPath(KPI_LIVE_BANNER_MODULE_KEY)) && method === 'PATCH';
    });
    expect(patchCall).toBeTruthy();
    const patchInit = patchCall![1] as RequestInit | undefined;
    const patchHeaders =
      patchInit?.headers instanceof Headers
        ? Object.fromEntries(patchInit.headers.entries())
        : (patchInit?.headers as Record<string, string> | undefined);
    expect(patchHeaders).toMatchObject({ 'If-Match': 'W/"0"' });
  });

  it('parcours e2e : erreur chargement → Recharger la configuration (AC-MODULES-SAVE-FIX)', async () => {
    vi.stubEnv('VITE_LIVE_AUTH', 'true');
    const fetchMock = buildModulesFetchMock({ kpiGetFailsFirst: true });
    vi.stubGlobal('fetch', fetchMock);

    renderAdminModulesRoute();

    const main = await screen.findByTestId('shell-zone-main');
    await waitFor(() => {
      expect(within(main).getByTestId('admin-modules-save-error')).toBeTruthy();
    });

    fireEvent.click(within(main).getByTestId('admin-modules-reload-config'));

    await waitFor(() => {
      expect(within(main).getByTestId('admin-modules-server-source')).toBeTruthy();
    });
  });
});
