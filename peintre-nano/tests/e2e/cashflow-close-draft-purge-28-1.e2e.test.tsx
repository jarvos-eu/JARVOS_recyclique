// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { DEMO_AUTH_STUB_SITE_ID } from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { CashflowCloseWizard } from '../../src/domains/cashflow/CashflowCloseWizard';
import {
  addTicketLine,
  attachCashflowDraftSessionPersistence,
  CASHFLOW_DRAFT_SESSION_STORAGE_PREFIX,
  getCashflowDraftSnapshot,
  resetCashflowDraft,
} from '../../src/domains/cashflow/cashflow-draft-store';
import '../../src/registry';
import '../../src/styles/tokens.css';
import {
  comptageModuleEnabledJson,
  denominationCountResponseForTotal,
  FIXTURE_CASH_DENOMINATIONS,
} from '../unit/fixtures/cash-denominations-api';

const SESSION_ID = '00000000-0000-4000-8000-000000000099';
const USER_KEY = 'demo-close-purge-28-1';

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

function sessionJson() {
  return {
    id: SESSION_ID,
    operator_id: 'op1',
    site_id: DEMO_AUTH_STUB_SITE_ID,
    initial_amount: 50,
    current_amount: 75,
    status: 'open',
    opened_at: '2026-01-01T00:00:00Z',
    total_sales: 25,
    total_donations: 0,
    total_weight_out: 0,
    totals: { sales_completed: 25, refunds: 0, net: 25 },
    closing_preview_theoretical_amount: 75,
  };
}

function mockFetchResponse(body: unknown, ok = true, status = 200) {
  return {
    ok,
    status,
    headers: { get: () => null },
    text: async () => (typeof body === 'string' ? body : JSON.stringify(body)),
  };
}

function buildCloseFetchMock() {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = requestUrl(input);
    const method = (init?.method ?? 'GET').toUpperCase();

    if (url.includes('/v1/cash-sessions/current')) {
      return Promise.resolve(mockFetchResponse(sessionJson()));
    }
    if (url.includes('/module-config/comptage-pieces-billets')) {
      return Promise.resolve(mockFetchResponse(comptageModuleEnabledJson()));
    }
    if (url.includes('/v1/cash-denominations')) {
      return Promise.resolve(mockFetchResponse(FIXTURE_CASH_DENOMINATIONS));
    }
    if (url.includes('/denomination-count')) {
      return Promise.resolve(mockFetchResponse(denominationCountResponseForTotal(7500)));
    }
    if (method === 'POST' && url.includes('/close')) {
      return Promise.resolve(
        mockFetchResponse({
          id: SESSION_ID,
          status: 'closed',
          anomaly_close_sheet: false,
          close_sheet_pdf_url: null,
        }),
      );
    }
    return Promise.resolve(mockFetchResponse({}));
  });
}

async function runCloseWizardToSuccess(): Promise<void> {
  await waitFor(() => expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy());
  fireEvent.click(screen.getByRole('button', { name: /Continuer vers le comptage grille/i }));
  await waitFor(() => expect(screen.getByTestId('cashflow-denomination-grid')).toBeTruthy());
  fireEvent.click(screen.getByTestId('cashflow-denomination-continue'));
  await waitFor(() => expect(screen.getByTestId('cashflow-close-verify')).toBeTruthy());
  fireEvent.click(screen.getByTestId('cashflow-verify-continue'));
  await waitFor(() => expect(screen.getByTestId('cashflow-close-variance-step')).toBeTruthy());
  fireEvent.click(screen.getByTestId('cashflow-close-variance-continue'));
  await waitFor(() => expect(screen.getByTestId('cashflow-close-review')).toBeTruthy());
  fireEvent.click(screen.getByTestId('cashflow-close-review-confirm'));
  await waitFor(() => expect(screen.getByTestId('cashflow-close-pin')).toBeTruthy());
  fireEvent.change(screen.getByLabelText(/PIN step-up/i), { target: { value: '1234' } });
  fireEvent.click(screen.getByTestId('cashflow-close-submit'));
  await waitFor(() => expect(screen.getByTestId('cashflow-close-success')).toBeTruthy());
}

beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    configurable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }),
  });
});

describe('Story 28.1 — purge brouillon après clôture (REV-CAISSE-02)', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    sessionStorage.clear();
    resetCashflowDraft();
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
    vi.useRealTimers();
    sessionStorage.clear();
    resetCashflowDraft();
    window.history.pushState({}, '', '/');
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    cleanup();
  });

  it('vide le brouillon ticket en mémoire et sessionStorage après clôture réussie', async () => {
    const detach = attachCashflowDraftSessionPersistence(USER_KEY);
    addTicketLine({
      category: 'EEE-1',
      quantity: 1,
      weight: 1,
      unitPrice: 12.5,
      totalPrice: 12.5,
    });
    vi.advanceTimersByTime(400);
    detach();

    const storageKey = `${CASHFLOW_DRAFT_SESSION_STORAGE_PREFIX}:${USER_KEY}`;
    expect(getCashflowDraftSnapshot().lines.length).toBe(1);
    expect(sessionStorage.getItem(storageKey)).not.toBeNull();

    vi.stubGlobal('fetch', buildCloseFetchMock());

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await runCloseWizardToSuccess();

    expect(getCashflowDraftSnapshot().lines.length).toBe(0);
    expect(getCashflowDraftSnapshot().totalAmount).toBe(0);
    const persisted = sessionStorage.getItem(storageKey);
    expect(persisted).not.toBeNull();
    expect(JSON.parse(persisted!).lines).toEqual([]);
  });
});
