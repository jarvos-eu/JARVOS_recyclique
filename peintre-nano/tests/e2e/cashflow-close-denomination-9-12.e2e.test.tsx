// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { DEMO_AUTH_STUB_SITE_ID } from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { CashflowCloseWizard } from '../../src/domains/cashflow/CashflowCloseWizard';
import '../../src/registry';
import '../../src/styles/tokens.css';
import {
  comptageModuleEnabledJson,
  denominationCountResponseForTotal,
  FIXTURE_CASH_DENOMINATIONS,
} from '../unit/fixtures/cash-denominations-api';

const SESSION_ID = '00000000-0000-4000-8000-000000000099';

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

function buildModuleOnFetchMock(opts?: { anomalyOnClose?: boolean }) {
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
      const raw = init?.headers;
      const getH = (k: string): string => {
        if (raw instanceof Headers) return raw.get(k) ?? '';
        if (raw && typeof raw === 'object') return String((raw as Record<string, string>)[k] ?? '');
        return '';
      };
      expect(getH('X-Step-Up-Pin')).toBe('1234');
      expect(getH('Idempotency-Key').length).toBeGreaterThan(0);
      return Promise.resolve(
        mockFetchResponse({
          id: SESSION_ID,
          status: 'closed',
          anomaly_close_sheet: opts?.anomalyOnClose ?? false,
          close_sheet_pdf_url: opts?.anomalyOnClose ? 'https://example.test/close-sheet.pdf' : null,
        }),
      );
    }

    return Promise.resolve(mockFetchResponse({}));
  });
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

describe('E2E — clôture caisse module comptage (Story 9.12)', () => {
  beforeEach(() => {
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
    window.history.pushState({}, '', '/');
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    cleanup();
  });

  it('parcours complet : grille → vérif → relecture → PIN → close + relais 6.9', async () => {
    const fetchMock = buildModuleOnFetchMock({ anomalyOnClose: false });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy());
    await waitFor(() =>
      expect(screen.getByRole('button', { name: /Continuer vers le comptage grille/i })).toBeTruthy(),
    );

    fireEvent.click(screen.getByRole('button', { name: /Continuer vers le comptage grille/i }));
    await waitFor(() => expect(screen.getByTestId('cashflow-denomination-grid')).toBeTruthy());

    expect(screen.getByTestId('cashflow-denomination-rules')).toBeTruthy();
    expect(screen.queryByTestId('cashflow-close-actual-amount')).toBeNull();

    const mainGrid = screen.getByTestId('cashflow-denomination-grid-main');
    expect(within(mainGrid).getByTestId('cashflow-denom-row-EUR_20000')).toBeTruthy();
    expect(within(mainGrid).queryByTestId('cashflow-denom-row-EUR_50000')).toBeNull();
    expect(screen.getByTestId('cashflow-denom-row-EUR_50000')).toBeTruthy();

    fireEvent.click(screen.getByTestId('cashflow-denomination-continue'));
    await waitFor(() => expect(screen.getByTestId('cashflow-close-verify')).toBeTruthy());

    fireEvent.click(screen.getByTestId('cashflow-verify-continue'));
    await waitFor(() => expect(screen.getByTestId('cashflow-close-variance-step')).toBeTruthy());

    fireEvent.click(screen.getByTestId('cashflow-close-variance-continue'));
    await waitFor(() => expect(screen.getByTestId('cashflow-close-review')).toBeTruthy());

    fireEvent.click(screen.getByTestId('cashflow-close-review-confirm'));
    await waitFor(() => expect(screen.getByTestId('cashflow-close-pin')).toBeTruthy());

    const pinInput = screen.getByLabelText(/PIN step-up/i);
    fireEvent.change(pinInput, { target: { value: '1234' } });
    fireEvent.input(pinInput, { target: { value: '1234' } });
    fireEvent.click(screen.getByTestId('cashflow-close-submit'));

    await waitFor(() => expect(screen.getByTestId('cashflow-close-success')).toBeTruthy());
    expect(screen.getByTestId('cashflow-close-relay-epic8').textContent).toMatch(/Recyclique/);
    expect(screen.queryByTestId('cashflow-close-pdf-anomaly')).toBeNull();

    const putCalls = fetchMock.mock.calls.filter(
      (c) => requestUrl(c[0]).includes('/denomination-count') && (c[1]?.method ?? 'GET').toUpperCase() === 'PUT',
    );
    expect(putCalls.length).toBeGreaterThan(0);

    const closeCalls = fetchMock.mock.calls.filter(
      (c) => requestUrl(c[0]).includes('/close') && (c[1]?.method ?? 'GET').toUpperCase() === 'POST',
    );
    expect(closeCalls.length).toBe(1);
  });

  it('relecture obligatoire : onglet PIN désactivé sans confirmation', async () => {
    vi.stubGlobal('fetch', buildModuleOnFetchMock());

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy());
    await waitFor(() =>
      expect(within(screen.getByTestId('flow-renderer-cashflow-close')).getByRole('tab', { name: /6\. Confirmer/i })).toBeTruthy(),
    );

    const flow = screen.getByTestId('flow-renderer-cashflow-close');
    const pinTab = within(flow).getByRole('tab', { name: /6\. Confirmer/i }) as HTMLButtonElement;
    expect(pinTab.disabled).toBe(true);
  });

  it('PDF anomalie proposé uniquement si closeSession signale anomaly_close_sheet', async () => {
    const fetchMock = buildModuleOnFetchMock({ anomalyOnClose: true });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

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
    expect(screen.getByTestId('cashflow-close-pdf-anomaly')).toBeTruthy();
  });

  it('erreur COMPTAGE_REQUIRED affichée sans masquer le code', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      const base = buildModuleOnFetchMock();
      if (method === 'POST' && url.includes('/close')) {
        return Promise.resolve(
          mockFetchResponse(
            {
              detail: 'Grille de comptage requise avant clôture.',
              code: 'COMPTAGE_REQUIRED',
            },
            false,
            400,
          ),
        );
      }
      return base(input, init);
    });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

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

    await waitFor(() => expect(screen.getByTestId('cashflow-close-submit-error')).toBeTruthy());
    expect(screen.getByTestId('cashflow-close-submit-error').textContent).toMatch(/COMPTAGE_REQUIRED|comptage/i);
    expect(screen.queryByTestId('cashflow-close-success')).toBeNull();
  });
});
