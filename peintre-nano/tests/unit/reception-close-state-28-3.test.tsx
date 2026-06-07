// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { ReceptionNominalWizard } from '../../src/domains/reception/ReceptionNominalWizard';
import '../../src/registry';

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

describe('Story 28.3 — état post-clôture ticket', () => {
  beforeEach(() => {
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

  it('après clôture : bandeau résumé, cockpit démonté, CTA nouveau ticket', async () => {
    const posteId = 'poste-close-28-3';
    const ticketId = 'ticket-close-28-3';
    let ticketStatus: 'opened' | 'closed' = 'opened';

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
      if (url.includes('/v1/reception/tickets') && method === 'POST' && !url.includes('/close')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: ticketId }),
        } as Response);
      }
      if (url.includes(`/v1/reception/tickets/${ticketId}/close`) && method === 'POST') {
        ticketStatus = 'closed';
        return Promise.resolve({ ok: true, status: 200, text: async () => '{}' } as Response);
      }
      if (url.includes(`/v1/reception/tickets/${ticketId}`) && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({
              id: ticketId,
              poste_id: posteId,
              benevole_username: 'vol',
              created_at: '2026-06-07T10:00:00Z',
              closed_at: ticketStatus === 'closed' ? '2026-06-07T11:00:00Z' : null,
              status: ticketStatus,
              lignes: [
                {
                  id: 'ligne-1',
                  ticket_id: ticketId,
                  category_id: 'cat-1',
                  category_label: 'Bois',
                  poids_kg: 2.5,
                  destination: 'MAGASIN',
                  notes: null,
                  is_exit: false,
                },
              ],
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

    fireEvent.click(screen.getByTestId('reception-close-ticket'));

    await waitFor(() => {
      expect(screen.getByTestId('reception-ticket-closed-summary')).toBeTruthy();
    });
    expect(screen.queryByTestId('reception-cockpit-layout')).toBeNull();
    expect(screen.queryByTestId('reception-close-ticket')).toBeNull();
    expect(screen.getByTestId('reception-create-ticket')).toBeTruthy();
    expect(screen.getByTestId('reception-ticket-closed-summary').textContent ?? '').toMatch(/Ticket clôturé/i);
    expect(screen.getByTestId('reception-ticket-closed-summary').textContent ?? '').toMatch(/2\.50 kg/);
  });

  it('peut créer un nouveau ticket après clôture sur le même poste', async () => {
    const posteId = 'poste-new-ticket-28-3';
    const ticketId1 = 'ticket-1-28-3';
    const ticketId2 = 'ticket-2-28-3';
    let ticketStatus: 'opened' | 'closed' = 'opened';
    let activeTicketId = ticketId1;

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
      if (url.includes('/v1/reception/tickets') && method === 'POST' && !url.includes('/close')) {
        activeTicketId = ticketId2;
        ticketStatus = 'opened';
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: ticketId2 }),
        } as Response);
      }
      if (url.includes(`/v1/reception/tickets/${ticketId1}/close`) && method === 'POST') {
        ticketStatus = 'closed';
        return Promise.resolve({ ok: true, status: 200, text: async () => '{}' } as Response);
      }
      if (url.includes('/v1/reception/tickets/') && method === 'GET') {
        const tid = url.includes(ticketId2) ? ticketId2 : ticketId1;
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({
              id: tid,
              poste_id: posteId,
              benevole_username: '',
              created_at: '',
              closed_at: tid === ticketId1 && ticketStatus === 'closed' ? '2026-06-07T11:00:00Z' : null,
              status: tid === ticketId1 ? ticketStatus : 'opened',
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
    fireEvent.click(screen.getByTestId('reception-close-ticket'));
    await waitFor(() => {
      expect(screen.getByTestId('reception-create-ticket')).toBeTruthy();
    });

    fireEvent.click(screen.getByTestId('reception-create-ticket'));
    await waitFor(() => {
      expect(screen.getByTestId('reception-cockpit-layout')).toBeTruthy();
    });
    expect(screen.queryByTestId('reception-ticket-closed-summary')).toBeNull();
    expect(activeTicketId).toBe(ticketId2);
  });
});
