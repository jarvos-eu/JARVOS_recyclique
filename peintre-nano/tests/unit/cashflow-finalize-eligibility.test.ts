import { describe, expect, it } from 'vitest';
import { evaluateCashflowFinalizeEligibility } from '../../src/domains/cashflow/cashflow-finalize-eligibility';
import type { CashflowDraftState } from '../../src/domains/cashflow/cashflow-draft-store';

function draftSlice(
  overrides: Partial<
    Pick<
      CashflowDraftState,
      'widgetDataState' | 'cashSessionIdInput' | 'activeHeldSaleId' | 'lines' | 'totalAmount'
    >
  > = {},
): Pick<
  CashflowDraftState,
  'widgetDataState' | 'cashSessionIdInput' | 'activeHeldSaleId' | 'lines' | 'totalAmount'
> {
  return {
    widgetDataState: 'NOMINAL',
    cashSessionIdInput: '',
    activeHeldSaleId: null,
    lines: [],
    totalAmount: 0,
    ...overrides,
  };
}

const sampleLine = {
  id: 'l1',
  category: 'EEE-1',
  quantity: 1,
  weight: 1,
  unitPrice: 10,
  totalPrice: 10,
};

describe('evaluateCashflowFinalizeEligibility (Story 28.1 / REV-05 / REV-06)', () => {
  const sadCases: Array<{
    readonly label: string;
    readonly draft: ReturnType<typeof draftSlice>;
    readonly pmReady: boolean;
    readonly pmLoading: boolean;
    readonly pmError: string | null;
    readonly blockedSubstring: string;
  }> = [
    {
      label: 'DATA_STALE bloque encaissement (REV-06)',
      draft: draftSlice({
        widgetDataState: 'DATA_STALE',
        cashSessionIdInput: 'sess-1',
        lines: [sampleLine],
        totalAmount: 10,
      }),
      pmReady: true,
      pmLoading: false,
      pmError: null,
      blockedSubstring: 'périmées',
    },
    {
      label: 'ticket vide sans montant (REV-05)',
      draft: draftSlice({ cashSessionIdInput: 'sess-1' }),
      pmReady: true,
      pmLoading: false,
      pmError: null,
      blockedSubstring: 'articles',
    },
    {
      label: 'lignes sans session ni held (REV-05)',
      draft: draftSlice({ lines: [sampleLine], totalAmount: 10 }),
      pmReady: true,
      pmLoading: false,
      pmError: null,
      blockedSubstring: 'Session caisse non résolue',
    },
    {
      label: 'moyens de paiement indisponibles (REV-06)',
      draft: draftSlice({
        cashSessionIdInput: 'sess-1',
        lines: [sampleLine],
        totalAmount: 10,
      }),
      pmReady: false,
      pmLoading: false,
      pmError: null,
      blockedSubstring: 'Moyens de paiement indisponibles',
    },
    {
      label: 'erreur chargement moyens de paiement',
      draft: draftSlice({
        cashSessionIdInput: 'sess-1',
        lines: [sampleLine],
        totalAmount: 10,
      }),
      pmReady: false,
      pmLoading: false,
      pmError: 'Erreur réseau options paiement',
      blockedSubstring: 'Erreur réseau options paiement',
    },
    {
      label: 'chargement moyens de paiement en cours (pmLoading)',
      draft: draftSlice({
        cashSessionIdInput: 'sess-1',
        lines: [sampleLine],
        totalAmount: 10,
      }),
      pmReady: false,
      pmLoading: true,
      pmError: null,
      blockedSubstring: 'Chargement des moyens de paiement',
    },
  ];

  it.each(sadCases)('$label', ({ draft, pmReady, pmLoading, pmError, blockedSubstring }) => {
    const result = evaluateCashflowFinalizeEligibility(draft, pmReady, pmLoading, pmError);
    expect(result.canFinalize).toBe(false);
    expect(result.blockedReason).toContain(blockedSubstring);
  });

  it('held sale sans cashSessionIdInput local reste encaissable', () => {
    const result = evaluateCashflowFinalizeEligibility(
      draftSlice({
        activeHeldSaleId: 'held-uuid',
        lines: [sampleLine],
        totalAmount: 10,
      }),
      true,
      false,
      null,
    );
    expect(result.canFinalize).toBe(true);
    expect(result.blockedReason).toBeNull();
  });

  it('GET courant ouvert sans cashSessionIdInput local reste encaissable (reprise hub)', () => {
    const result = evaluateCashflowFinalizeEligibility(
      draftSlice({ lines: [sampleLine], totalAmount: 10 }),
      true,
      false,
      null,
      'open-session-from-server',
    );
    expect(result.canFinalize).toBe(true);
    expect(result.blockedReason).toBeNull();
  });

  it('session + lignes + moyens de paiement OK → encaissable', () => {
    const result = evaluateCashflowFinalizeEligibility(
      draftSlice({
        cashSessionIdInput: 'sess-1',
        lines: [sampleLine],
        totalAmount: 10,
      }),
      true,
      false,
      null,
    );
    expect(result.canFinalize).toBe(true);
    expect(result.blockedReason).toBeNull();
  });
});
