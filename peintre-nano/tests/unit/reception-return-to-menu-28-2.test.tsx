// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { ReceptionNominalWizard } from '../../src/domains/reception/ReceptionNominalWizard';
import '../../src/registry';

const spaNavigateToMock = vi.fn();

vi.mock('../../src/app/demo/spa-navigate', () => ({
  spaNavigateTo: (path: string) => spaNavigateToMock(path),
}));

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

describe('Story 28.2 — réception hub inactif retour menu', () => {
  beforeEach(() => {
    spaNavigateToMock.mockClear();
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
  });

  it('affiche Retour au menu sur hub sans poste et navigue vers /dashboard', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = requestUrl(input);
      const empty = '[]';
      const emptyObj = '{}';
      if (url.includes('/v1/reception/categories')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => empty,
          json: async () => [],
        } as Response);
      }
      if (url.includes('/v1/stats/live')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => emptyObj,
          json: async () => ({}),
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => emptyObj,
        json: async () => ({}),
      } as Response);
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

    const returnBtn = await screen.findByTestId('reception-return-to-menu');
    expect(returnBtn.textContent).toMatch(/Retour au menu/i);
    fireEvent.click(returnBtn);

    await waitFor(() => {
      expect(spaNavigateToMock).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('masque Retour au menu quand un poste est ouvert', async () => {
    const posteId = 'poste-open-28-2';
    const ticketId = 'ticket-open-28-2';
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/reception/postes/open') && method === 'POST') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: posteId, status: 'open' }),
          json: async () => ({ id: posteId, status: 'open' }),
        } as Response);
      }
      if (url.includes('/v1/reception/tickets') && method === 'POST') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: ticketId }),
          json: async () => ({ id: ticketId }),
        } as Response);
      }
      if (url.includes('/v1/reception/categories')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => '[]',
          json: async () => [],
        } as Response);
      }
      if (url.includes('/v1/stats/live')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => '{}',
          json: async () => ({}),
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '{}',
        json: async () => ({}),
      } as Response);
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
      expect(screen.getByTestId('reception-poste-id').getAttribute('title')).toBe(posteId);
    });

    expect(screen.queryByTestId('reception-return-to-menu')).toBeNull();
    expect(spaNavigateToMock).not.toHaveBeenCalled();
  });

  it('réaffiche Retour au menu après fermeture du poste', async () => {
    const posteId = 'poste-close-28-2';
    const ticketId = 'ticket-close-28-2';
    let ticketStatus: 'opened' | 'closed' = 'opened';

    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/reception/postes/open') && method === 'POST') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: posteId, status: 'open' }),
          json: async () => ({ id: posteId, status: 'open' }),
        } as Response);
      }
      if (url.includes('/v1/reception/tickets') && method === 'POST' && !url.includes('/close')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: ticketId }),
          json: async () => ({ id: ticketId }),
        } as Response);
      }
      if (url.includes(`/v1/reception/tickets/${ticketId}/close`) && method === 'POST') {
        ticketStatus = 'closed';
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => '{}',
          json: async () => ({}),
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
              closed_at: ticketStatus === 'closed' ? '2026-06-07T12:00:00Z' : null,
              status: ticketStatus,
              lignes: [],
            }),
          json: async () => ({
            id: ticketId,
            poste_id: posteId,
            benevole_username: '',
            created_at: '',
            closed_at: ticketStatus === 'closed' ? '2026-06-07T12:00:00Z' : null,
            status: ticketStatus,
            lignes: [],
          }),
        } as Response);
      }
      if (url.includes(`/v1/reception/postes/${posteId}/close`) && method === 'POST') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => '{}',
          json: async () => ({}),
        } as Response);
      }
      if (url.includes('/v1/reception/categories')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => '[]',
          json: async () => [],
        } as Response);
      }
      if (url.includes('/v1/stats/live')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => '{}',
          json: async () => ({}),
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '{}',
        json: async () => ({}),
      } as Response);
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
      expect(screen.getByTestId('reception-poste-id').getAttribute('title')).toBe(posteId);
    });
    expect(screen.queryByTestId('reception-return-to-menu')).toBeNull();

    fireEvent.click(screen.getByTestId('reception-close-ticket'));
    await waitFor(() => {
      expect(screen.getByTestId('reception-close-poste')).toBeTruthy();
    });

    fireEvent.click(screen.getByTestId('reception-close-poste'));
    await waitFor(() => {
      expect(screen.queryByTestId('reception-poste-id')).toBeNull();
    });

    const returnBtn = screen.getByTestId('reception-return-to-menu');
    expect(returnBtn.textContent).toMatch(/Retour au menu/i);
    expect(spaNavigateToMock).not.toHaveBeenCalled();
  });

  it('affiche Retour au menu sur contexte bloqué et navigue vers /dashboard', () => {
    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u1' },
      envelope: createDefaultDemoEnvelope({
        runtimeStatus: 'forbidden',
        restrictionMessage: 'Accès réception refusé',
      }),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <ReceptionNominalWizard widgetProps={{}} />
      </RootProviders>,
    );

    expect(screen.getByTestId('reception-context-blocked')).toBeTruthy();
    const returnBtn = screen.getByTestId('reception-return-to-menu');
    expect(returnBtn.textContent).toMatch(/Retour au menu/i);
    fireEvent.click(returnBtn);
    expect(spaNavigateToMock).toHaveBeenCalledWith('/dashboard');
  });
});
