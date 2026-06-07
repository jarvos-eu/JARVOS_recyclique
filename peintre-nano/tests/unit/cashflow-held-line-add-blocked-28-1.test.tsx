// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { resetCoalescedGetCurrentOpenCashSessionForTests } from '../../src/domains/cashflow/caisse-current-session-coalesce';
import {
  applyServerHeldSaleToDraft,
  resetCashflowDraft,
} from '../../src/domains/cashflow/cashflow-draft-store';
import { CashflowNominalWizard } from '../../src/domains/cashflow/CashflowNominalWizard';
import '../../src/registry';

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

describe('Story 28.1 — cashflow-held-line-add-blocked', () => {
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
    applyServerHeldSaleToDraft({
      id: 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee',
      total_amount: 12.5,
      items: [
        {
          category: 'EEE-1',
          quantity: 1,
          weight: 1,
          unit_price: 12.5,
          total_price: 12.5,
        },
      ],
    });
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
  });

  it('affiche l’alerte et désactive l’ajout de ligne quand un held sale est actif (REV-10)', async () => {
    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: 'u1' },
      envelope: createDefaultDemoEnvelope(),
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <CashflowNominalWizard widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('cashflow-held-line-add-blocked')).toBeTruthy();
    });
    expect((screen.getByTestId('cashflow-add-line') as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByTestId('cashflow-input-total') as HTMLInputElement).disabled).toBe(true);
  });
});
