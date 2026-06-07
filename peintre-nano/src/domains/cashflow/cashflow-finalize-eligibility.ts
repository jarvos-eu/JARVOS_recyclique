import type { CashflowDraftState } from './cashflow-draft-store';

export type CashflowFinalizeEligibility = {
  readonly canFinalize: boolean;
  readonly blockedReason: string | null;
};

/**
 * Prédicat partagé kiosque / wizard — held sale : session portée par le ticket serveur,
 * pas besoin de `cashSessionIdInput` local pour débloquer l’encaissement.
 */
export function evaluateCashflowFinalizeEligibility(
  draft: Pick<
    CashflowDraftState,
    'widgetDataState' | 'cashSessionIdInput' | 'activeHeldSaleId' | 'lines' | 'totalAmount'
  >,
  paymentMethodsReady: boolean,
  paymentMethodsLoading: boolean,
  paymentMethodsError: string | null,
  /** GET /v1/cash-sessions/current — autorité serveur si session ouverte (reprise hub sans recollage brouillon). */
  serverOpenSessionId?: string | null,
): CashflowFinalizeEligibility {
  if (draft.widgetDataState === 'DATA_STALE') {
    return {
      canFinalize: false,
      blockedReason: 'Données ticket périmées — actualisez le ticket avant encaissement.',
    };
  }
  if (draft.lines.length === 0 || draft.totalAmount <= 0) {
    return {
      canFinalize: false,
      blockedReason: 'Ajoutez des articles et un montant positif au ticket.',
    };
  }
  const sessionReady =
    draft.cashSessionIdInput.trim().length > 0 ||
    Boolean(draft.activeHeldSaleId?.trim()) ||
    Boolean(serverOpenSessionId?.trim());
  if (!sessionReady) {
    return {
      canFinalize: false,
      blockedReason: 'Session caisse non résolue — reprenez le poste ou actualisez la session.',
    };
  }
  if (paymentMethodsLoading) {
    return { canFinalize: false, blockedReason: 'Chargement des moyens de paiement…' };
  }
  if (paymentMethodsError) {
    return { canFinalize: false, blockedReason: paymentMethodsError };
  }
  if (!paymentMethodsReady) {
    return {
      canFinalize: false,
      blockedReason: 'Moyens de paiement indisponibles — vérifiez le paramétrage comptable.',
    };
  }
  return { canFinalize: true, blockedReason: null };
}

/** UUID session pour POST vente : brouillon local, sinon GET courant ouvert. */
export function resolveCashflowSaleSessionId(
  cashSessionIdInput: string,
  serverOpenSessionId?: string | null,
): string {
  const local = cashSessionIdInput.trim();
  if (local) return local;
  return serverOpenSessionId?.trim() ?? '';
}
