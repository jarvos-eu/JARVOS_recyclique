// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { LIVE_AUTH_ACCESS_TOKEN_STORAGE_KEY } from '../../src/api/recyclique-auth-client';
import { SharedWorkstationEffectiveModulesProvider } from '../../src/domains/shared-workstation/SharedWorkstationEffectiveModulesProvider';
import { filterNavigation } from '../../src/runtime/filter-navigation-for-context';
import type { NavigationManifest } from '../../types/navigation-manifest';
import type { ContextEnvelopeStub } from '../../types/context-envelope';

const { fetchSharedWorkstationEffectiveModules } = vi.hoisted(() => ({
  fetchSharedWorkstationEffectiveModules: vi.fn(),
}));

vi.mock('../../src/api/shared-workstation-effective-modules-client', () => ({
  fetchSharedWorkstationEffectiveModules,
}));

vi.mock('../../src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider', () => ({
  useSharedWorkstationOperatorSession: () => ({
    loading: false,
    hasDevice: true,
    operatorSessionActive: true,
    refreshSessionStatus: vi.fn(),
  }),
}));

const navManifest: NavigationManifest = {
  version: '1',
  entries: [
    {
      id: 'bandeau-live-sandbox',
      routeKey: 'bandeau-live-sandbox',
      pageKey: 'bandeau-live-sandbox',
      requiredPermissionKeys: ['recyclique.exploitation.view-live-band'],
    },
    {
      id: 'root-home',
      routeKey: 'root-home',
      pageKey: 'demo-home',
    },
  ],
};

const envelope: ContextEnvelopeStub = {
  schemaVersion: '1',
  siteId: 'site-1',
  activeRegisterId: null,
  permissions: {
    permissionKeys: ['recyclique.exploitation.view-live-band'],
  },
  issuedAt: Date.now(),
  runtimeStatus: 'ok',
};

function Probe() {
  return <span data-testid="probe">ok</span>;
}

afterEach(() => {
  cleanup();
  sessionStorage.clear();
  vi.clearAllMocks();
});

describe('SharedWorkstationEffectiveModulesProvider (Story 27.7)', () => {
  it('fetch modules effectifs au montage post-PIN', async () => {
    sessionStorage.setItem(LIVE_AUTH_ACCESS_TOKEN_STORAGE_KEY, 'tok');
    fetchSharedWorkstationEffectiveModules.mockResolvedValue({
      ok: true,
      module_keys: ['kpi-live-banner'],
      computed_at: '2026-05-30T12:00:00Z',
      site_id: 's1',
      device_id: 'd1',
      operator_user_id: 'o1',
    });

    render(
      <SharedWorkstationEffectiveModulesProvider>
        <Probe />
      </SharedWorkstationEffectiveModulesProvider>,
    );

    await waitFor(() => {
      expect(fetchSharedWorkstationEffectiveModules).toHaveBeenCalledWith('tok');
    });
  });

  it('masque navigation bandeau-live si module absent de la liste serveur', () => {
    const filtered = filterNavigation(navManifest, envelope, {
      effectiveModuleKeys: [],
    });
    const ids = filtered.entries.map((e) => e.id);
    expect(ids).not.toContain('bandeau-live-sandbox');
    expect(ids).toContain('root-home');
  });

  it('conserve navigation bandeau-live si module présent serveur', () => {
    const filtered = filterNavigation(navManifest, envelope, {
      effectiveModuleKeys: ['kpi-live-banner'],
    });
    const ids = filtered.entries.map((e) => e.id);
    expect(ids).toContain('bandeau-live-sandbox');
  });
});
