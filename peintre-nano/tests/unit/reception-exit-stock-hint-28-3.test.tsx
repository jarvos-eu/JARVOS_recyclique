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

async function reachPoidsStepThroughVisibleSelection(): Promise<HTMLInputElement> {
  await screen.findByTestId('reception-kiosk-category-grid');
  for (let attempt = 0; attempt < 8; attempt += 1) {
    const inputs = screen.queryAllByLabelText('Poids (kg)');
    const input = inputs.find((el) => el.tagName === 'INPUT');
    if (input) return input as HTMLInputElement;

    const grid = screen.getByTestId('reception-kiosk-category-grid');
    const tile = grid.querySelector(
      'button[data-testid^="reception-kiosk-category-"]',
    ) as HTMLButtonElement | null;
    if (!tile) throw new Error('Aucune tuile categorie visible.');
    fireEvent.click(tile);
  }
  return (await screen.findByLabelText('Poids (kg)')) as HTMLInputElement;
}

describe('Story 28.3 — découverte sortie de stock', () => {
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

  it('affiche le hint sortie de stock avec ticket ouvert', async () => {
    const posteId = 'poste-exit-hint-28-3';
    const ticketId = 'ticket-exit-hint-28-3';
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

    const hint = screen.getByTestId('reception-exit-stock-hint');
    expect(hint.textContent ?? '').toMatch(/Sortie de stock/i);
    expect(hint.textContent ?? '').toMatch(/=/);
  });

  it('toggle isExit via raccourci = sur le champ poids', async () => {
    const posteId = 'poste-eq-28-3';
    const ticketId = 'ticket-eq-28-3';
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
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify([{ id: 'cat-1', name: 'Articles' }]),
        } as Response);
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
    await waitFor(() => expect(screen.getByTestId('reception-ticket-id').getAttribute('title')).toBe(ticketId));

    const poidsInput = await reachPoidsStepThroughVisibleSelection();
    poidsInput.focus();
    await waitFor(() => expect(document.activeElement).toBe(poidsInput));
    expect(screen.getByTestId('reception-switch-is-exit')).toBeTruthy();
    const destinationInput = screen.getByRole('textbox', { name: 'Destination' }) as HTMLInputElement;
    expect(destinationInput.value).toBe('Magasin');

    fireEvent.keyDown(poidsInput, { key: '=', code: 'Equal', bubbles: true, cancelable: true });

    await waitFor(() => expect(destinationInput.value).toBe('Recyclage'));
  });
});
