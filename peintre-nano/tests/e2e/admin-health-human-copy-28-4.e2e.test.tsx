// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { RuntimeDemoApp } from '../../src/app/demo/RuntimeDemoApp';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { CONTEXT_ACTIVE_SITE_DISPLAY_NAME_KEY } from '../../src/runtime/context-presentation-keys';
import '../../src/registry';
import '../../src/styles/tokens.css';

const siteDisplayName = 'Site Pilote Recyclique E2E';

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

function okJson(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: { get: () => null },
    text: async () => JSON.stringify(body),
    json: async () => body,
  } as Response;
}

const healthSystemPayload = {
  status: 'success',
  system_health: {
    overall_status: 'healthy',
    anomalies_detected: 0,
    critical_anomalies: 0,
    scheduler_running: false,
    active_tasks: 0,
    timestamp: '2026-06-07T12:00:00Z',
  },
  anomalies: {
    cash_anomalies: [],
    sync_anomalies: [],
    auth_anomalies: [],
    classification_anomalies: [],
    timestamp: '2026-06-07T12:00:00Z',
  },
  recommendations: [
    {
      type: 'cash_control',
      priority: 'high',
      title: 'Renforcer les contrôles caisse',
      description: 'Action directe possible dans l’application.',
      actions: ['Former les équipes'],
    },
    {
      type: 'preventive_database_maintenance',
      priority: 'low',
      title: 'Maintenance BDD',
      description: 'Bonnes pratiques hors application.',
      actions: ['Archiver les données anciennes'],
    },
  ],
  scheduler_status: { running: false, tasks: [], total_tasks: 0 },
};

function buildHealthFetchMock() {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = requestUrl(input);
    const method = (init?.method ?? 'GET').toUpperCase();

    if (url.includes('/v1/admin/health') && !url.includes('test-notifications') && method === 'GET') {
      return Promise.resolve(okJson(healthSystemPayload));
    }

    if (url.includes('/v1/admin/health/test-notifications') && method === 'POST') {
      return Promise.resolve(
        okJson({
          status: 'unavailable',
          message: 'Fonction documentée comme désactivée sur le serveur.',
        }),
      );
    }

    if (url.includes('/v1/admin/sessions/metrics') && method === 'GET') {
      return Promise.resolve(
        okJson({
          success: true,
          metrics: {
            total_operations: 0,
            refresh_success_count: 0,
            refresh_failure_count: 0,
            refresh_success_rate_percent: 0,
            logout_forced_count: 0,
            logout_manual_count: 0,
            active_sessions_estimate: 0,
            latency_metrics: {},
            error_breakdown: {},
            ip_breakdown: {},
            site_breakdown: {},
            time_period_hours: 24,
            timestamp: 1713000000,
          },
        }),
      );
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
      return Promise.resolve(okJson({ tickets_open: 2, ca: 10.5 }));
    }

    if (url.includes('/v1/context/envelope/refresh') && method === 'POST') {
      return Promise.resolve(okJson({ ok: true, envelope: {} }));
    }

    return Promise.resolve(okJson({}));
  });
}

function renderAdminHealthRoute() {
  const auth = createMockAuthAdapter({
    session: { authenticated: true, userId: 'u-admin-health-28-4-e2e' },
    envelope: createDefaultDemoEnvelope({
      presentationLabels: {
        [CONTEXT_ACTIVE_SITE_DISPLAY_NAME_KEY]: siteDisplayName,
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

describe('E2E — Story 28.4 admin santé copie humaine (REV-ADMIN-05, REV-TRANSVERSE-04/05)', () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
    window.history.pushState({}, '', '/admin/health');
  });

  afterEach(() => {
    window.history.pushState({}, '', '/');
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
    cleanup();
  });

  it('RuntimeDemoApp /admin/health : libellé alertes, badges responsable, nom site (AC-HEALTH-COPY, AC-HEALTH-RECO)', async () => {
    vi.stubEnv('VITE_LIVE_AUTH', 'true');
    vi.stubGlobal('fetch', buildHealthFetchMock());

    renderAdminHealthRoute();

    const main = await screen.findByTestId('shell-zone-main');
    await waitFor(() => {
      expect(within(main).getByTestId('admin-system-health-widget')).toBeTruthy();
    });

    expect(within(main).getByText('Tester les alertes')).toBeTruthy();
    expect(within(main).queryByText(/endpoint.*test notifications/i)).toBeNull();

    const widget = within(main).getByTestId('admin-system-health-widget');
    const badges = await within(widget).findAllByTestId('admin-health-reco-responsible-badge');
    expect(badges.map((b) => b.textContent)).toContain('À faire dans l’application');
    expect(badges.map((b) => b.textContent)).toContain('Informatif — rien à faire maintenant');
    expect(within(widget).getByText(/Responsable : À faire dans l’application/)).toBeTruthy();
    expect(within(widget).getByText(siteDisplayName)).toBeTruthy();
  });

  it('parcours e2e : clic « Tester les alertes » déclenche POST test-notifications', async () => {
    vi.stubEnv('VITE_LIVE_AUTH', 'true');
    const fetchMock = buildHealthFetchMock();
    vi.stubGlobal('fetch', fetchMock);

    renderAdminHealthRoute();

    const main = await screen.findByTestId('shell-zone-main');
    const testBtn = await within(main).findByTestId('admin-system-health-test-notifications');
    fireEvent.click(testBtn);

    await waitFor(() => {
      const postCall = fetchMock.mock.calls.find(([inp, init]) => {
        const url = requestUrl(inp as RequestInfo);
        const method = (init?.method ?? 'GET').toUpperCase();
        return url.includes('/v1/admin/health/test-notifications') && method === 'POST';
      });
      expect(postCall).toBeTruthy();
    });
  });
});
