// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { ReceptionNominalWizard } from '../../src/domains/reception/ReceptionNominalWizard';
import {
  DEFAULT_RECEPTION_COCKPIT_LAYOUT,
  RECEPTION_COCKPIT_LAYOUT_STORAGE_KEY,
  buildCockpitGridTemplateColumns,
  loadReceptionCockpitLayout,
  saveReceptionCockpitLayout,
} from '../../src/domains/reception/reception-cockpit-layout-storage';
import '../../src/registry';

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

describe('Story 28.3 — redimensionnement cockpit (AC-LAYOUT-RESIZE)', () => {
  beforeEach(() => {
    window.localStorage.removeItem(RECEPTION_COCKPIT_LAYOUT_STORAGE_KEY);
    vi.stubGlobal(
      'matchMedia',
      vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    );
    vi.stubGlobal(
      'ResizeObserver',
      class {
        observe(): void {}
        unobserve(): void {}
        disconnect(): void {}
      },
    );
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    window.localStorage.removeItem(RECEPTION_COCKPIT_LAYOUT_STORAGE_KEY);
  });

  it('persiste les ratios colonnes après drag poignée gauche', async () => {
    const posteId = 'poste-resize-28-3';
    const ticketId = 'ticket-resize-28-3';

    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/reception/postes/open') && method === 'POST') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: posteId }),
        } as Response);
      }
      if (url.includes('/v1/reception/tickets') && method === 'POST') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: ticketId }),
        } as Response);
      }
      if (url.includes(`/v1/reception/tickets/${ticketId}`) && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({
              id: ticketId,
              poste_id: posteId,
              benevole_username: '',
              created_at: '',
              closed_at: null,
              status: 'opened',
              lignes: [],
            }),
        } as Response);
      }
      if (url.includes('/v1/reception/categories')) {
        return Promise.resolve({ ok: true, status: 200, text: async () => '[]' } as Response);
      }
      if (url.includes('/v1/stats/live')) {
        return Promise.resolve({ ok: true, status: 200, text: async () => '{}' } as Response);
      }
      return Promise.resolve({ ok: true, status: 200, text: async () => '{}' } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u1' },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <ReceptionNominalWizard widgetProps={{}} />
      </RootProviders>,
    );

    fireEvent.click(screen.getByTestId('reception-open-poste'));
    await waitFor(() => {
      expect(screen.getByTestId('reception-cockpit-layout')).toBeTruthy();
    });

    const layout = screen.getByTestId('reception-cockpit-layout');
    vi.spyOn(layout, 'getBoundingClientRect').mockReturnValue({
      width: 1000,
      height: 600,
      top: 0,
      left: 0,
      right: 1000,
      bottom: 600,
      x: 0,
      y: 0,
      toJSON: () => ({}),
    });

    const handle = screen.getByTestId('reception-cockpit-resize-left');
    handle.setPointerCapture = vi.fn();
    handle.hasPointerCapture = vi.fn().mockReturnValue(true);
    handle.releasePointerCapture = vi.fn();
    fireEvent.pointerDown(handle, { clientX: 300, pointerId: 1, buttons: 1 });
    fireEvent.pointerMove(handle, { clientX: 450, pointerId: 1, buttons: 1 });
    fireEvent.pointerUp(handle, { clientX: 450, pointerId: 1 });

    await waitFor(() => {
      const stored = loadReceptionCockpitLayout();
      expect(stored).not.toEqual(DEFAULT_RECEPTION_COCKPIT_LAYOUT);
    });
    expect(screen.getByTestId('reception-cockpit-resize-right')).toBeTruthy();
  });

  it('recharge les ratios persistés au remontage du cockpit', async () => {
    const storedLayout = { leftPct: 35, centerPct: 42 };
    saveReceptionCockpitLayout(storedLayout);

    const posteId = 'poste-remount-28-3';
    const ticketId = 'ticket-remount-28-3';
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/reception/postes/open') && method === 'POST') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: posteId }),
        } as Response);
      }
      if (url.includes('/v1/reception/tickets') && method === 'POST') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: ticketId }),
        } as Response);
      }
      if (url.includes(`/v1/reception/tickets/${ticketId}`) && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({
              id: ticketId,
              poste_id: posteId,
              benevole_username: '',
              created_at: '',
              closed_at: null,
              status: 'opened',
              lignes: [],
            }),
        } as Response);
      }
      if (url.includes('/v1/reception/categories')) {
        return Promise.resolve({ ok: true, status: 200, text: async () => '[]' } as Response);
      }
      if (url.includes('/v1/stats/live')) {
        return Promise.resolve({ ok: true, status: 200, text: async () => '{}' } as Response);
      }
      return Promise.resolve({ ok: true, status: 200, text: async () => '{}' } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u1' },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    const { unmount } = render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <ReceptionNominalWizard widgetProps={{}} />
      </RootProviders>,
    );

    fireEvent.click(screen.getByTestId('reception-open-poste'));
    await waitFor(() => {
      const layout = screen.getByTestId('reception-cockpit-layout');
      expect(layout.style.gridTemplateColumns).toBe(buildCockpitGridTemplateColumns(storedLayout));
    });

    unmount();
    cleanup();

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <ReceptionNominalWizard widgetProps={{}} />
      </RootProviders>,
    );

    fireEvent.click(screen.getByTestId('reception-open-poste'));
    await waitFor(() => {
      const layout = screen.getByTestId('reception-cockpit-layout');
      expect(layout.style.gridTemplateColumns).toBe(buildCockpitGridTemplateColumns(storedLayout));
    });
  });
});
