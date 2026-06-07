// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { AdminSystemHealthWidget } from '../../src/domains/admin-config/AdminSystemHealthWidget';
import {
  createDefaultDemoEnvelope,
  DEMO_AUTH_STUB_SITE_ID,
  getDefaultDemoAuthAdapter,
} from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import {
  AdminSystemHealthApiError,
  fetchAdminHealthSystem,
  postAdminHealthTestNotifications,
} from '../../src/api/admin-system-health-client';
import { listSitesForAdmin } from '../../src/api/admin-sites-client';
import { CONTEXT_ACTIVE_SITE_DISPLAY_NAME_KEY } from '../../src/runtime/context-presentation-keys';
import '../../src/registry';

vi.mock('../../src/api/live-snapshot-client', async (importOriginal) => {
  const mod = await importOriginal<typeof import('../../src/api/live-snapshot-client')>();
  return {
    ...mod,
    fetchLiveSnapshot: vi.fn().mockResolvedValue({
      ok: true,
      snapshot: { observed_at: '2026-04-13T12:00:00Z', effective_open_state: 'open' },
      correlationId: 'test-corr',
      degradedEmpty: false,
    }),
  };
});

vi.mock('../../src/api/admin-sites-client', () => ({
  listSitesForAdmin: vi.fn().mockResolvedValue({ ok: true, data: [] }),
}));

vi.mock('../../src/api/admin-system-health-client', () => ({
  AdminSystemHealthApiError: class extends Error {
    constructor(
      readonly status: number,
      message: string,
    ) {
      super(message);
      this.name = 'AdminSystemHealthApiError';
    }
  },
  fetchAdminHealthSystem: vi.fn(),
  postAdminHealthTestNotifications: vi.fn().mockResolvedValue({
    status: 'unavailable',
    message: 'Fonction documentée comme désactivée sur le serveur.',
  }),
  fetchAdminSessionMetrics: vi.fn().mockResolvedValue({
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
}));

vi.mock('../../src/api/dashboard-legacy-stats-client', () => ({
  DashboardLegacyApiError: class extends Error {},
  fetchUnifiedLiveStats: vi.fn().mockResolvedValue({ tickets_open: 2 }),
}));

vi.mock('../../src/api/recyclique-auth-client', () => ({
  postRecycliqueContextEnvelopeRefresh: vi.fn().mockResolvedValue({ ok: true, envelope: {} }),
}));

beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    configurable: true,
    value: () => ({
      matches: false,
      media: '',
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }),
  });
});

afterEach(() => {
  cleanup();
});

beforeEach(() => {
  vi.mocked(fetchAdminHealthSystem).mockReset();
  vi.mocked(postAdminHealthTestNotifications).mockReset();
  vi.mocked(postAdminHealthTestNotifications).mockResolvedValue({
    status: 'unavailable',
    message: 'Fonction documentée comme désactivée sur le serveur.',
  });
  vi.mocked(listSitesForAdmin).mockReset();
  vi.mocked(listSitesForAdmin).mockResolvedValue({ ok: true, data: [] });
});

describe('AdminSystemHealthWidget human copy 28-4', () => {
  it('affiche le libellé « Tester les alertes » et le badge responsable', async () => {
    vi.mocked(fetchAdminHealthSystem).mockResolvedValue({
      status: 'success',
      system_health: {
        overall_status: 'healthy',
        anomalies_detected: 0,
        critical_anomalies: 0,
        scheduler_running: false,
        active_tasks: 0,
        timestamp: '2026-04-13T12:00:00Z',
      },
      anomalies: {
        cash_anomalies: [],
        sync_anomalies: [],
        auth_anomalies: [],
        classification_anomalies: [],
        timestamp: '2026-04-13T12:00:00Z',
      },
      recommendations: [
        {
          type: 'cash_control',
          priority: 'high',
          title: 'Renforcer les contrôles caisse',
          description: 'Action directe possible.',
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
    });

    const adapter = {
      ...getDefaultDemoAuthAdapter(),
      getAccessToken: () => 'test-token',
      getContextEnvelope: () => ({
        ...getDefaultDemoAuthAdapter().getContextEnvelope(),
        presentationLabels: { [CONTEXT_ACTIVE_SITE_DISPLAY_NAME_KEY]: 'Site Pilote Recyclique' },
      }),
    };

    render(
      <RootProviders authAdapter={adapter}>
        <AdminSystemHealthWidget />
      </RootProviders>,
    );

    await screen.findByTestId('admin-system-health-test-notifications');
    expect(screen.getByText('Tester les alertes')).toBeTruthy();
    expect(screen.queryByText(/endpoint.*test notifications/i)).toBeNull();

    const badges = await screen.findAllByTestId('admin-health-reco-responsible-badge');
    expect(badges.map((b) => b.textContent)).toContain('À faire dans l’application');
    expect(badges.map((b) => b.textContent)).toContain('Informatif — rien à faire maintenant');
    expect(screen.getByText(/Responsable : À faire dans l’application/)).toBeTruthy();
    expect(screen.getByText(/Site Pilote Recyclique/)).toBeTruthy();
  });

  it('badge « équipe technique / hébergeur » pour reco sync_monitoring', async () => {
    vi.mocked(fetchAdminHealthSystem).mockResolvedValue({
      status: 'success',
      system_health: {
        overall_status: 'warning',
        anomalies_detected: 1,
        critical_anomalies: 0,
        scheduler_running: true,
        active_tasks: 1,
        timestamp: '2026-04-13T12:00:00Z',
      },
      anomalies: {
        cash_anomalies: [],
        sync_anomalies: [{ type: 'stale', message: 'Sync en retard' }],
        auth_anomalies: [],
        classification_anomalies: [],
        timestamp: '2026-04-13T12:00:00Z',
      },
      recommendations: [
        {
          type: 'sync_monitoring',
          priority: 'medium',
          title: 'Surveiller la synchronisation',
          description: 'Écarts détectés sur les flux de données.',
          actions: ['Vérifier les journaux côté hébergeur'],
        },
      ],
      scheduler_status: { running: true, tasks: [], total_tasks: 1 },
    });

    const adapter = {
      ...getDefaultDemoAuthAdapter(),
      getAccessToken: () => 'test-token',
    };

    render(
      <RootProviders authAdapter={adapter}>
        <AdminSystemHealthWidget />
      </RootProviders>,
    );

    const badges = await screen.findAllByTestId('admin-health-reco-responsible-badge');
    expect(badges.map((b) => b.textContent)).toContain('À faire par l’équipe technique / hébergeur');
    expect(screen.getByText(/Responsable : À faire par l’équipe technique \/ hébergeur/)).toBeTruthy();
  });

  it('affiche un message FR explicite sur 403 test notifications (session admin)', async () => {
    vi.mocked(fetchAdminHealthSystem).mockResolvedValue({
      status: 'success',
      system_health: {
        overall_status: 'healthy',
        anomalies_detected: 0,
        critical_anomalies: 0,
        scheduler_running: false,
        active_tasks: 0,
        timestamp: '2026-04-13T12:00:00Z',
      },
      anomalies: {
        cash_anomalies: [],
        sync_anomalies: [],
        auth_anomalies: [],
        classification_anomalies: [],
        timestamp: '2026-04-13T12:00:00Z',
      },
      recommendations: [],
      scheduler_status: { running: false, tasks: [], total_tasks: 0 },
    });
    vi.mocked(postAdminHealthTestNotifications).mockRejectedValue(
      new AdminSystemHealthApiError(403, 'Accès refusé'),
    );

    const adapter = {
      ...getDefaultDemoAuthAdapter(),
      getAccessToken: () => 'test-token',
    };

    render(
      <RootProviders authAdapter={adapter}>
        <AdminSystemHealthWidget />
      </RootProviders>,
    );

    const testBtn = await screen.findByTestId('admin-system-health-test-notifications');
    fireEvent.click(testBtn);

    expect(
      await screen.findByText(
        /Accès refusé \(403\) — cette vérification peut exiger une session administrateur renforcée côté serveur\./,
      ),
    ).toBeTruthy();
  });

  it('tronque le UUID site dans le contexte opérateur sans presentationLabels', async () => {
    vi.mocked(fetchAdminHealthSystem).mockResolvedValue({
      status: 'success',
      system_health: {
        overall_status: 'healthy',
        anomalies_detected: 0,
        critical_anomalies: 0,
        scheduler_running: false,
        active_tasks: 0,
        timestamp: '2026-04-13T12:00:00Z',
      },
      anomalies: {
        cash_anomalies: [],
        sync_anomalies: [],
        auth_anomalies: [],
        classification_anomalies: [],
        timestamp: '2026-04-13T12:00:00Z',
      },
      recommendations: [],
      scheduler_status: { running: false, tasks: [], total_tasks: 0 },
    });

    const adapter = {
      ...getDefaultDemoAuthAdapter(),
      getAccessToken: () => 'test-token',
      getContextEnvelope: () =>
        createDefaultDemoEnvelope({
          siteId: DEMO_AUTH_STUB_SITE_ID,
          presentationLabels: {},
        }),
    };

    render(
      <RootProviders authAdapter={adapter}>
        <AdminSystemHealthWidget />
      </RootProviders>,
    );

    const truncated = `${DEMO_AUTH_STUB_SITE_ID.slice(0, 8)}…`;
    expect(await screen.findByText(truncated)).toBeTruthy();
    expect(screen.queryByText(DEMO_AUTH_STUB_SITE_ID)).toBeNull();
  });
});
