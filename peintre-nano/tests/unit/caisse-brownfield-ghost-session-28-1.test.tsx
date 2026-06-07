// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { CaisseBrownfieldDashboardWidget } from '../../src/domains/cashflow/CaisseBrownfieldDashboardWidget';
import { resetCoalescedGetCurrentOpenCashSessionForTests } from '../../src/domains/cashflow/caisse-current-session-coalesce';
import { setCashSessionIdInput, resetCashflowDraft } from '../../src/domains/cashflow/cashflow-draft-store';
import '../../src/registry';

const GHOST_SESSION_ID = 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee';

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

describe('Story 28.1 — session fantôme enveloppe (data-resolved-session-id)', () => {
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
    resetCashflowDraft();
    resetCoalescedGetCurrentOpenCashSessionForTests();
    setCashSessionIdInput(GHOST_SESSION_ID);
  });

  it('n’expose pas l’ID session enveloppe quand GET courant est absent (REV-01)', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL) => {
        const url = requestUrl(input);
        if (url.includes('/v1/cash-sessions/current')) {
          return { ok: true, status: 200, text: async () => 'null' } as Response;
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
        <CaisseBrownfieldDashboardWidget widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => {
      const row = screen.getByTestId('caisse-legacy-register-row');
      expect(row.getAttribute('data-resolved-session-id')).toBe('');
      expect(row.getAttribute('data-server-session-loading')).toBe('false');
    });
  });
});
