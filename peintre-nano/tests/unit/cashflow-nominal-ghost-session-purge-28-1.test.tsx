// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, render, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { resetCoalescedGetCurrentOpenCashSessionForTests } from '../../src/domains/cashflow/caisse-current-session-coalesce';
import { CashflowNominalWizard } from '../../src/domains/cashflow/CashflowNominalWizard';
import {
  getCashflowDraftSnapshot,
  resetCashflowDraft,
  setCashSessionIdInput,
} from '../../src/domains/cashflow/cashflow-draft-store';
import '../../src/registry';

const GHOST_SESSION_ID = 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee';
const LIVE_SESSION_ID = '11111111-2222-4333-8444-555555555555';

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

describe('Story 28.1 — purge openedSessionId brouillon (CashflowNominalWizard)', () => {
  afterEach(() => {
    cleanup();
    resetCashflowDraft();
    resetCoalescedGetCurrentOpenCashSessionForTests();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

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
    resetCashflowDraft();
    resetCoalescedGetCurrentOpenCashSessionForTests();
    setCashSessionIdInput(GHOST_SESSION_ID);
  });

  it('purge cashSessionIdInput quand GET courant est absent (session fantôme locale)', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL) => {
        const url = requestUrl(input);
        if (url.includes('/v1/cash-sessions/current')) {
          return { ok: true, status: 200, text: async () => 'null' } as Response;
        }
        if (url.includes('/v1/categories/')) {
          return { ok: true, status: 200, text: async () => '[]' } as Response;
        }
        return { ok: false, status: 404, text: async () => 'not found' } as Response;
      }),
    );

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u1' },
      envelope: createDefaultDemoEnvelope({ cashSessionId: GHOST_SESSION_ID }),
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <CashflowNominalWizard widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(getCashflowDraftSnapshot().cashSessionIdInput).toBe('');
    });
  });

  it('ne purge pas cashSessionIdInput tant que GET courant est en chargement', async () => {
    let resolveCurrent: ((value: Response) => void) | undefined;
    const currentPending = new Promise<Response>((resolve) => {
      resolveCurrent = resolve;
    });

    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL) => {
        const url = requestUrl(input);
        if (url.includes('/v1/cash-sessions/current')) {
          return currentPending;
        }
        if (url.includes('/v1/categories/')) {
          return { ok: true, status: 200, text: async () => '[]' } as Response;
        }
        return { ok: false, status: 404, text: async () => 'not found' } as Response;
      }),
    );

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u1' },
      envelope: createDefaultDemoEnvelope({ cashSessionId: GHOST_SESSION_ID }),
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <CashflowNominalWizard widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(getCashflowDraftSnapshot().cashSessionIdInput).toBe(GHOST_SESSION_ID);
    });

    resolveCurrent!({ ok: true, status: 200, text: async () => 'null' } as Response);

    await waitFor(() => {
      expect(getCashflowDraftSnapshot().cashSessionIdInput).toBe('');
    });
  });

  it('recolle cashSessionIdInput sur GET courant ouvert même si brouillon/enveloppe fantômes (HITL reprise)', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL) => {
        const url = requestUrl(input);
        if (url.includes('/v1/cash-sessions/current')) {
          return {
            ok: true,
            status: 200,
            text: async () =>
              JSON.stringify({
                id: LIVE_SESSION_ID,
                status: 'open',
                register_id: 'reg-main',
                opened_at: '2026-06-07T10:00:00Z',
              }),
          } as Response;
        }
        if (url.includes('/v1/categories/')) {
          return { ok: true, status: 200, text: async () => '[]' } as Response;
        }
        return { ok: false, status: 404, text: async () => 'not found' } as Response;
      }),
    );

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u1' },
      envelope: createDefaultDemoEnvelope({ cashSessionId: GHOST_SESSION_ID }),
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <CashflowNominalWizard widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(getCashflowDraftSnapshot().cashSessionIdInput).toBe(LIVE_SESSION_ID);
    });
  });
});
