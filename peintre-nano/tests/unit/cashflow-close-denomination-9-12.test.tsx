// @vitest-environment jsdom
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
} from './fixtures/cash-denominations-api';

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

function buildModuleOnFetchMock(opts?: {
  anomalyOnClose?: boolean;
  showImages?: boolean;
  denominationCount?: ReturnType<typeof denominationCountResponseForTotal>;
}) {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = requestUrl(input);
    const method = (init?.method ?? 'GET').toUpperCase();

    if (url.includes('/v1/cash-sessions/current')) {
      return Promise.resolve(mockFetchResponse(sessionJson()));
    }

    if (url.includes('/module-config/comptage-pieces-billets')) {
      return Promise.resolve(mockFetchResponse(comptageModuleEnabledJson(opts?.showImages ?? true)));
    }

    if (url.includes('/v1/cash-denominations')) {
      return Promise.resolve(mockFetchResponse(FIXTURE_CASH_DENOMINATIONS));
    }

    if (url.includes('/denomination-count')) {
      return Promise.resolve(
        mockFetchResponse(opts?.denominationCount ?? denominationCountResponseForTotal(7500)),
      );
    }

    if (method === 'POST' && url.includes('/close')) {
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

async function advanceModuleWizardToReviewConfirm(): Promise<void> {
  await waitFor(() => expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy());
  await waitFor(() =>
    expect(screen.getByRole('button', { name: /Continuer vers le comptage grille/i })).toBeTruthy(),
  );
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

afterEach(() => {
  vi.restoreAllMocks();
  cleanup();
});

describe('Story 9.12 — module comptage activé', () => {
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

  it('affiche la grille, les 4 règles, et pas de actual_amount manuel', async () => {
    vi.stubGlobal('fetch', buildModuleOnFetchMock());

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy();
    });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Continuer vers le comptage grille/i })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole('button', { name: /Continuer vers le comptage grille/i }));

    await waitFor(() => {
      expect(screen.getByTestId('cashflow-denomination-grid')).toBeTruthy();
    });

    expect(screen.getByTestId('cashflow-denomination-rules')).toBeTruthy();
    expect(screen.queryByTestId('cashflow-close-actual-amount')).toBeNull();
    const mainGrid = screen.getByTestId('cashflow-denomination-grid-main');
    expect(within(mainGrid).getByTestId('cashflow-denom-row-EUR_20000')).toBeTruthy();
    expect(within(mainGrid).queryByTestId('cashflow-denom-row-EUR_50000')).toBeNull();
    expect(screen.getByTestId('cashflow-denomination-rares')).toBeTruthy();
    expect(screen.getByTestId('cashflow-denom-row-EUR_50000')).toBeTruthy();
  });

  it('exige la relecture avant PIN même si écart nul', async () => {
    vi.stubGlobal('fetch', buildModuleOnFetchMock());

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy();
    });

    await waitFor(() => {
      expect(within(screen.getByTestId('flow-renderer-cashflow-close')).getByRole('tab', { name: /6\. Confirmer/i })).toBeTruthy();
    });

    const flow = screen.getByTestId('flow-renderer-cashflow-close');
    const pinTab = within(flow).getByRole('tab', { name: /6\. Confirmer/i }) as HTMLButtonElement;
    expect(pinTab.disabled).toBe(true);
  });

  it('bloque le saut d’étapes : onglet Vérifier inaccessible sans continuer depuis la grille', async () => {
    vi.stubGlobal('fetch', buildModuleOnFetchMock());

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy());
    fireEvent.click(screen.getByRole('button', { name: /Continuer vers le comptage grille/i }));
    await waitFor(() => expect(screen.getByTestId('cashflow-denomination-grid')).toBeTruthy());

    const flow = screen.getByTestId('flow-renderer-cashflow-close');
    const verifyTab = within(flow).getByRole('tab', { name: /3\. Vérifier/i }) as HTMLButtonElement;
    expect(verifyTab.disabled).toBe(true);
  });

  it('réinitialise la relecture confirmée au retour grille après PIN', async () => {
    vi.stubGlobal('fetch', buildModuleOnFetchMock());

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await advanceModuleWizardToReviewConfirm();

    const flow = screen.getByTestId('flow-renderer-cashflow-close');
    fireEvent.click(within(flow).getByRole('tab', { name: /2\. Grille/i }));
    await waitFor(() => expect(screen.getByTestId('cashflow-denomination-grid')).toBeTruthy());

    const pinTab = within(flow).getByRole('tab', { name: /6\. Confirmer/i }) as HTMLButtonElement;
    expect(pinTab.disabled).toBe(true);
  });

  it('réinitialise la relecture si quantités modifiées après confirmation', async () => {
    vi.stubGlobal('fetch', buildModuleOnFetchMock());

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await advanceModuleWizardToReviewConfirm();

    const flow = screen.getByTestId('flow-renderer-cashflow-close');
    fireEvent.click(within(flow).getByRole('tab', { name: /2\. Grille/i }));
    await waitFor(() => expect(screen.getByTestId('cashflow-denomination-grid')).toBeTruthy());

    fireEvent.click(screen.getByTestId('cashflow-denom-plus-EUR_100'));

    const pinTab = within(flow).getByRole('tab', { name: /6\. Confirmer/i }) as HTMLButtonElement;
    expect(pinTab.disabled).toBe(true);
  });

  it('affiche alerte PIN renforcée si seuil D33 dépassé', async () => {
    const highVariance = {
      ...denominationCountResponseForTotal(10_000),
      variance_cents: 2500,
    };
    vi.stubGlobal('fetch', buildModuleOnFetchMock({ denominationCount: highVariance }));

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await advanceModuleWizardToReviewConfirm();
    expect(screen.getByTestId('cashflow-close-pin-alert').textContent).toMatch(/seuil site \(2\.00 €\)/);
  });

  it('affiche alerte PIN si coupure 500 € dans le breakdown', async () => {
    const with500 = {
      ...denominationCountResponseForTotal(7500),
      breakdown: [
        { code: 'EUR_50000', quantity: 1, unit_value_cents: 50000, line_total_cents: 50000 },
        { code: 'EUR_2000', quantity: 0, unit_value_cents: 2000, line_total_cents: 0 },
      ],
    };
    vi.stubGlobal('fetch', buildModuleOnFetchMock({ denominationCount: with500 }));

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await advanceModuleWizardToReviewConfirm();
    expect(screen.getByTestId('cashflow-close-pin-alert').textContent).toMatch(/500 €/);
  });

  it('show_images true affiche pictos, false masque (AC11)', async () => {
    vi.stubGlobal('fetch', buildModuleOnFetchMock({ showImages: true }));

    const { unmount } = render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy());
    fireEvent.click(screen.getByRole('button', { name: /Continuer vers le comptage grille/i }));
    await waitFor(() => expect(screen.getByTestId('cashflow-denomination-grid')).toBeTruthy());
    expect(screen.getByTestId('cashflow-denom-picto-EUR_100')).toBeTruthy();
    unmount();
    cleanup();

    vi.stubGlobal('fetch', buildModuleOnFetchMock({ showImages: false }));
    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );
    await waitFor(() => expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy());
    fireEvent.click(screen.getByRole('button', { name: /Continuer vers le comptage grille/i }));
    await waitFor(() => expect(screen.getByTestId('cashflow-denomination-grid')).toBeTruthy());
    expect(screen.queryByTestId('cashflow-denom-picto-EUR_100')).toBeNull();
  });

  it('parcours complet : grille → relecture → close sans PDF si pas d’anomalie', async () => {
    const fetchMock = buildModuleOnFetchMock({ anomalyOnClose: false });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy();
    });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Continuer vers le comptage grille/i })).toBeTruthy();
    });

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
    expect(screen.getByTestId('cashflow-close-relay-epic8').textContent).toMatch(/Recyclique/);
    expect(screen.queryByTestId('cashflow-close-pdf-anomaly')).toBeNull();

    const putCalls = fetchMock.mock.calls.filter(
      (c) => requestUrl(c[0]).includes('/denomination-count') && (c[1]?.method ?? 'GET').toUpperCase() === 'PUT',
    );
    expect(putCalls.length).toBeGreaterThan(0);
  });

  it('propose le PDF uniquement sur anomalie (mock close)', async () => {
    const fetchMock = buildModuleOnFetchMock({ anomalyOnClose: true });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await advanceModuleWizardToReviewConfirm();

    fireEvent.change(screen.getByLabelText(/PIN step-up/i), { target: { value: '1234' } });
    fireEvent.click(screen.getByTestId('cashflow-close-submit'));

    await waitFor(() => expect(screen.getByTestId('cashflow-close-success')).toBeTruthy());
    expect(screen.getByTestId('cashflow-close-pdf-anomaly')).toBeTruthy();
  });

  it('affiche COMPTAGE_REQUIRED sur échec close (module actif)', async () => {
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

    await advanceModuleWizardToReviewConfirm();

    fireEvent.change(screen.getByLabelText(/PIN step-up/i), { target: { value: '1234' } });
    fireEvent.click(screen.getByTestId('cashflow-close-submit'));

    await waitFor(() => expect(screen.getByTestId('cashflow-close-submit-error')).toBeTruthy());
    expect(screen.getByTestId('cashflow-close-submit-error').textContent).toMatch(/COMPTAGE_REQUIRED|comptage/i);
  });
});

describe('Story 9.12 — parité legacy module off', () => {
  it('conserve actual_amount quand module désactivé (404 module-config)', async () => {
    vi.stubGlobal(
      'ResizeObserver',
      class {
        observe(): void {}
        unobserve(): void {}
        disconnect(): void {}
      },
    );

    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = requestUrl(input);
      if (url.includes('/module-config/comptage-pieces-billets')) {
        return Promise.resolve(mockFetchResponse({ detail: 'Not found' }, false, 404));
      }
      if (url.includes('/v1/cash-sessions/current')) {
        return Promise.resolve(mockFetchResponse(sessionJson()));
      }
      return Promise.resolve(mockFetchResponse({}));
    });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <RootProviders disableUserPrefsPersistence>
        <CashflowCloseWizard widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy());
    fireEvent.click(screen.getByRole('button', { name: /Continuer vers le comptage$/i }));
    expect(screen.getByTestId('cashflow-close-actual-amount')).toBeTruthy();
    expect(screen.queryByTestId('cashflow-denomination-grid')).toBeNull();
  });
});
