// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi, type ReactNode } from 'vitest';
import { MantineProvider } from '@mantine/core';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { ReceptionNominalWizard } from '../../src/domains/reception/ReceptionNominalWizard';
import { SharedWorkstationLockScreen } from '../../src/domains/shared-workstation/SharedWorkstationLockScreen';
import '../../src/registry';

const sessionMock = vi.hoisted(() => ({
  loading: false,
  hasDevice: true,
  operatorSessionActive: true,
  refreshSessionStatus: vi.fn(async () => true),
}));

vi.mock('../../src/api/shared-workstation-operator-pin-client', () => ({
  verifySharedWorkstationOperatorPin: vi.fn(),
}));

vi.mock('../../src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider', () => ({
  useSharedWorkstationOperatorSession: () => sessionMock,
  useOptionalSharedWorkstationOperatorSession: () => sessionMock,
  useSharedWorkstationLockRequired: () =>
    sessionMock.hasDevice && (sessionMock.loading || !sessionMock.operatorSessionActive),
  SharedWorkstationOperatorSessionProvider: ({ children }: { children: ReactNode }) => children,
}));

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

const SENSITIVE_TICKET_ID = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee';
const SENSITIVE_LIGNE_NOTE = 'note-confidentielle-brouillon-27-8';

describe('shared-workstation-reception-draft lock e2e (Story 27.8)', () => {
  beforeAll(() => {
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
    vi.stubGlobal(
      'ResizeObserver',
      class {
        observe(): void {}
        unobserve(): void {}
        disconnect(): void {}
      },
    );
  });

  beforeEach(() => {
    sessionMock.loading = false;
    sessionMock.hasDevice = true;
    sessionMock.operatorSessionActive = true;
    sessionMock.refreshSessionStatus.mockClear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it('lock screen sans fuite ticket/ligne dans le DOM', () => {
    render(
      <MantineProvider>
        <SharedWorkstationLockScreen />
      </MantineProvider>,
    );
    expect(screen.getByTestId('shared-workstation-lock-screen')).toBeTruthy();
    expect(screen.queryByTestId('reception-ticket-detail')).toBeNull();
    expect(screen.queryByTestId('reception-ligne-row')).toBeNull();
    expect(screen.queryByTestId('shared-workstation-reception-draft-panel')).toBeNull();
    expect(screen.queryByText(/brouillon en attente/i)).toBeNull();
  });

  it('wizard monté puis transition lock masque les données sensibles', async () => {
    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u1' },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();

      if (url.includes('/v1/shared-workstation/reception-draft') && method === 'GET') {
        return Promise.resolve({ ok: true, status: 204, text: async () => '' } as Response);
      }
      if (url.includes('/v1/reception/postes/open') && method === 'POST') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: 'poste-lock-e2e', status: 'opened' }),
        } as Response);
      }
      if (url.includes('/v1/reception/tickets') && method === 'POST' && !url.includes(SENSITIVE_TICKET_ID)) {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify({ id: SENSITIVE_TICKET_ID }),
        } as Response);
      }
      if (url.includes(`/v1/reception/tickets/${SENSITIVE_TICKET_ID}`) && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({
              id: SENSITIVE_TICKET_ID,
              poste_id: 'poste-lock-e2e',
              benevole_username: 'operateur-secret',
              created_at: '2026-05-30T10:00:00.000Z',
              closed_at: null,
              status: 'opened',
              lignes: [
                {
                  id: 'ligne-lock-e2e',
                  ticket_id: SENSITIVE_TICKET_ID,
                  category_id: 'cat-1',
                  category_label: 'Carton',
                  poids_kg: 4.2,
                  destination: 'MAGASIN',
                  notes: SENSITIVE_LIGNE_NOTE,
                  is_exit: false,
                },
              ],
            }),
        } as Response);
      }
      if (url.includes('/v1/reception/categories') && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify([{ id: 'cat-1', name: 'Carton', parent_id: null }]),
        } as Response);
      }
      return Promise.resolve({
        ok: false,
        status: 404,
        text: async () => 'not found',
      } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    function LockAwareShell({ locked }: { readonly locked: boolean }) {
      sessionMock.operatorSessionActive = !locked;
      const lockRequired =
        sessionMock.hasDevice && (sessionMock.loading || !sessionMock.operatorSessionActive);
      return (
        <>
          {lockRequired ? (
            <MantineProvider>
              <SharedWorkstationLockScreen />
            </MantineProvider>
          ) : null}
          {!lockRequired ? (
            <RootProviders authAdapter={auth} disableUserPrefsPersistence>
              <ReceptionNominalWizard widgetProps={{}} />
            </RootProviders>
          ) : null}
        </>
      );
    }

    const { rerender } = render(<LockAwareShell locked={false} />);

    fireEvent.click(screen.getByTestId('reception-open-poste'));
    await waitFor(() => {
      expect(screen.getByTestId('reception-poste-id').getAttribute('title')).toBe('poste-lock-e2e');
    });
    fireEvent.click(screen.getByTestId('reception-create-ticket'));
    await waitFor(() => {
      expect(screen.getByTestId('reception-nominal-wizard')).toBeTruthy();
    });
    expect(screen.getByTestId('reception-ticket-id').getAttribute('title')).toBe(SENSITIVE_TICKET_ID);

    rerender(<LockAwareShell locked={true} />);

    await waitFor(() => {
      expect(screen.queryByTestId('reception-nominal-wizard')).toBeNull();
    });
    expect(screen.getByTestId('shared-workstation-lock-screen')).toBeTruthy();
    expect(screen.queryByTestId('reception-ticket-id')).toBeNull();
    expect(screen.queryByTestId('reception-lignes-list')).toBeNull();
    expect(screen.queryByText(SENSITIVE_TICKET_ID)).toBeNull();
    expect(screen.queryByText(SENSITIVE_LIGNE_NOTE)).toBeNull();
    expect(screen.queryByText(/operateur-secret/i)).toBeNull();
    expect(document.body.textContent ?? '').not.toMatch(/note-confidentielle/i);
  });
});
