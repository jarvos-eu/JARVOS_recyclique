import { Alert, Button, Group, NumberInput, PasswordInput, Stack, Text, TextInput } from '@mantine/core';
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { recycliqueClientFailureFromSalesHttp } from '../../api/recyclique-api-error';
import { spaNavigateTo } from '../../app/demo/spa-navigate';
import {
  CLOSE_VARIANCE_TOLERANCE_EUR,
  DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR,
  buildDenominationUpsertLines,
  cashSessionCloseFailureMessage,
  computeLocalCountedCents,
  getCashDenominations,
  getCurrentOpenCashSession,
  getDenominationCount,
  needsVarianceComment,
  postCloseCashSession,
  putDenominationCount,
  quantitiesFromBreakdown,
  theoreticalCloseAmount,
  type CashDenominationV1,
  type CashSessionCurrentV1,
  type DenominationCountResponseV1,
} from '../../api/cash-session-client';
import { useComptageModuleConfig } from '../../api/comptage-module-config';
import { PERMISSION_CASHFLOW_NOMINAL } from '../../app/auth/default-demo-auth-adapter';
import { useAuthPort, useContextEnvelope } from '../../app/auth/AuthRuntimeProvider';
import { FlowRenderer } from '../../flows/FlowRenderer';
import type { RegisteredWidgetProps } from '../../registry/widget-registry';
import { CashflowClientErrorAlert } from './CashflowClientErrorAlert';
import { CashflowCloseReviewPanel } from './CashflowCloseReviewPanel';
import { CashflowCloseVerifyPanel } from './CashflowCloseVerifyPanel';
import { CashflowDenominationGridPanel } from './CashflowDenominationGridPanel';
import { CashflowOperationalSyncNotice } from './cashflow-operational-sync-notice';
import type { CashflowSubmitSurfaceError } from './cashflow-submit-error';
import { useCashflowDraft } from './cashflow-draft-store';
import classes from './CashflowCloseWizard.module.css';

const DENOMINATION_PUT_DEBOUNCE_MS = 500;

const RELAY_EPIC8_COPY =
  'Session fermée dans Recyclique. La mise en cohérence comptable avec Paheko est prise en charge par d’autres flux (synchronisation, hors périmètre de cet écran). Aucun état de synchronisation n’est affiché ici.';

type EntryBlock =
  | { readonly blocked: false }
  | { readonly blocked: true; readonly title: string; readonly body: string };

type DoneState =
  | null
  | {
      kind: 'closed';
      sessionId: string;
      anomalyCloseSheet?: boolean;
      closeSheetPdfUrl?: string | null;
    }
  | { kind: 'deleted'; message?: string };

function useCloseEntryBlock(): EntryBlock {
  const envelope = useContextEnvelope();
  return useMemo((): EntryBlock => {
    if (envelope.runtimeStatus === 'forbidden') {
      return {
        blocked: true,
        title: 'Contexte bloqué',
        body:
          envelope.restrictionMessage?.trim() ||
          'Accès refusé par le serveur (enveloppe « forbidden »).',
      };
    }
    if (envelope.runtimeStatus === 'degraded') {
      return {
        blocked: true,
        title: 'Contexte restreint',
        body:
          envelope.restrictionMessage?.trim() ||
          'Contexte dégradé — rafraîchir le contexte avant la clôture.',
      };
    }
    if (!envelope.siteId?.trim()) {
      return {
        blocked: true,
        title: 'Site actif non résolu',
        body: 'L’enveloppe ne fournit pas de site : la clôture ne peut pas continuer.',
      };
    }
    if (!envelope.permissions.permissionKeys.includes(PERMISSION_CASHFLOW_NOMINAL)) {
      return {
        blocked: true,
        title: 'Permission caisse absente',
        body: `Les permissions effectives ne contiennent pas « ${PERMISSION_CASHFLOW_NOMINAL} ».`,
      };
    }
    return { blocked: false };
  }, [envelope]);
}

function fmtEur(n: number): string {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(n);
}

function varianceCommentRequiredFromCents(varianceCents: number): boolean {
  return Math.abs(varianceCents) > Math.round(CLOSE_VARIANCE_TOLERANCE_EUR * 100);
}

function varianceExceedsD33Threshold(varianceCents: number): boolean {
  return Math.abs(varianceCents) > Math.round(DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR * 100);
}

function hasRare500EuroNote(denomCount: DenominationCountResponseV1): boolean {
  return denomCount.breakdown.some((line) => line.code === 'EUR_50000' && line.quantity > 0);
}

/**
 * Story 6.7 + extension 9.12 — clôture locale : legacy 3 panels ou parcours comptage 6 panels + succès.
 */
export function CashflowCloseWizard(_props: RegisteredWidgetProps): ReactNode {
  const entry = useCloseEntryBlock();
  const envelope = useContextEnvelope();
  const contextBinding = useMemo(
    () => ({ siteId: envelope.siteId, cashSessionId: envelope.cashSessionId }),
    [envelope.siteId, envelope.cashSessionId],
  );
  const auth = useAuthPort();
  const { loading: moduleConfigLoading, moduleEnabled, config: comptageConfig } =
    useComptageModuleConfig(auth, envelope.siteId);
  const draft = useCashflowDraft();
  const stale = draft.widgetDataState === 'DATA_STALE';
  const [tab, setTab] = useState(0);
  const [session, setSession] = useState<CashSessionCurrentV1 | null>(null);
  const [loadErr, setLoadErr] = useState<CashflowSubmitSurfaceError | null>(null);
  const [loading, setLoading] = useState(true);
  const [actualAmount, setActualAmount] = useState<number | string>('');
  const [varianceComment, setVarianceComment] = useState('');
  const [pin, setPin] = useState('');
  const [submitErr, setSubmitErr] = useState<CashflowSubmitSurfaceError | null>(null);
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState<DoneState>(null);

  const [denominations, setDenominations] = useState<CashDenominationV1[]>([]);
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [denomCount, setDenomCount] = useState<DenominationCountResponseV1 | null>(null);
  const [gridBusy, setGridBusy] = useState(false);
  const [gridErr, setGridErr] = useState<CashflowSubmitSurfaceError | null>(null);
  const [reviewConfirmed, setReviewConfirmed] = useState(false);
  const [maxAccessibleTab, setMaxAccessibleTab] = useState(0);
  const putDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const refreshSession = useCallback(async () => {
    setLoadErr(null);
    setLoading(true);
    try {
      const r = await getCurrentOpenCashSession(auth);
      if (!r.ok) {
        setSession(null);
        setLoadErr({ kind: 'api', failure: recycliqueClientFailureFromSalesHttp(r) });
        return;
      }
      setSession(r.session);
      if (r.session && !moduleEnabled) {
        const th = theoreticalCloseAmount(r.session);
        setActualAmount(th);
      } else if (!r.session) {
        setActualAmount('');
      }
    } finally {
      setLoading(false);
    }
  }, [auth, moduleEnabled]);

  const initDenominationState = useCallback(
    async (sessionId: string) => {
      const countRes = await getDenominationCount(sessionId, auth);
      if (countRes.ok) {
        setDenomCount(countRes.data);
        setDenominations(countRes.data.denominations);
        setQuantities(quantitiesFromBreakdown(countRes.data.denominations, countRes.data.breakdown));
        return;
      }
      const listRes = await getCashDenominations(auth);
      if (!listRes.ok) {
        setGridErr({ kind: 'api', failure: recycliqueClientFailureFromSalesHttp(listRes) });
        return;
      }
      setDenominations(listRes.denominations);
      const q: Record<string, number> = {};
      for (const d of listRes.denominations) q[d.code] = 0;
      setQuantities(q);
    },
    [auth],
  );

  useEffect(() => {
    if (entry.blocked) return;
    void refreshSession();
  }, [entry.blocked, refreshSession]);

  useEffect(() => {
    if (!moduleEnabled || !session?.id || moduleConfigLoading) return;
    void initDenominationState(session.id);
  }, [moduleEnabled, moduleConfigLoading, session?.id, initDenominationState]);

  useEffect(() => {
    return () => {
      if (putDebounceRef.current) clearTimeout(putDebounceRef.current);
    };
  }, []);

  const theoretical = session ? theoreticalCloseAmount(session) : 0;
  const actualNum = typeof actualAmount === 'number' ? actualAmount : parseFloat(String(actualAmount));
  const legacyCommentRequired =
    session && !moduleEnabled && !Number.isNaN(actualNum) && needsVarianceComment(actualNum, theoretical);

  const liveTotalCents = useMemo(
    () => computeLocalCountedCents(denominations, quantities),
    [denominations, quantities],
  );

  const flushDenominationPut = useCallback(async (): Promise<DenominationCountResponseV1 | null> => {
    if (!session?.id || denominations.length === 0) return null;
    if (putDebounceRef.current) {
      clearTimeout(putDebounceRef.current);
      putDebounceRef.current = null;
    }
    const body = { lines: buildDenominationUpsertLines(denominations, quantities) };
    const res = await putDenominationCount(session.id, body, auth);
    if (!res.ok) {
      setGridErr({ kind: 'api', failure: recycliqueClientFailureFromSalesHttp(res) });
      return null;
    }
    setGridErr(null);
    setDenomCount(res.data);
    return res.data;
  }, [auth, denominations, quantities, session?.id]);

  const scheduleDenominationPut = useCallback(() => {
    if (!session?.id || denominations.length === 0) return;
    if (putDebounceRef.current) clearTimeout(putDebounceRef.current);
    putDebounceRef.current = setTimeout(() => {
      putDebounceRef.current = null;
      void flushDenominationPut();
    }, DENOMINATION_PUT_DEBOUNCE_MS);
  }, [denominations.length, flushDenominationPut, session?.id]);

  const onQuantityChange = useCallback(
    (code: string, quantity: number) => {
      setQuantities((prev) => ({ ...prev, [code]: quantity }));
      setReviewConfirmed(false);
      setMaxAccessibleTab((prev) => Math.min(prev, 1));
      scheduleDenominationPut();
    },
    [scheduleDenominationPut],
  );

  const navigateToTab = useCallback(
    (index: number, opts?: { bumpMaxTo?: number }) => {
      if (moduleEnabled) {
        const bumping = opts?.bumpMaxTo !== undefined;
        if (!bumping && index > maxAccessibleTab) return;
        if (!bumping && index === 5 && !reviewConfirmed) return;
        if (reviewConfirmed && (index === 1 || index === 2)) {
          setReviewConfirmed(false);
        }
        if (opts !== undefined && opts.bumpMaxTo !== undefined) {
          setMaxAccessibleTab(opts.bumpMaxTo);
        }
        setTab(index);
        return;
      }
      setTab(index);
    },
    [moduleEnabled, maxAccessibleTab, reviewConfirmed],
  );

  const isModuleTabDisabled = useCallback(
    (index: number): boolean => {
      if (!moduleEnabled) return false;
      if (index > maxAccessibleTab) return true;
      if (index === 5 && !reviewConfirmed) return true;
      return false;
    },
    [moduleEnabled, maxAccessibleTab, reviewConfirmed],
  );

  const onGridContinue = async () => {
    setGridBusy(true);
    setGridErr(null);
    try {
      const data = await flushDenominationPut();
      if (!data) return;
      setDenomCount(data);
      navigateToTab(2, { bumpMaxTo: 2 });
    } finally {
      setGridBusy(false);
    }
  };

  const moduleCommentRequired =
    moduleEnabled && denomCount != null && varianceCommentRequiredFromCents(denomCount.variance_cents);

  const onSubmitClose = async () => {
    if (!session) return;
    const pinTrim = pin.trim();
    if (pinTrim.length < 4) {
      setSubmitErr({
        kind: 'local',
        message: 'Saisissez le PIN métier (step-up) pour confirmer la clôture.',
      });
      return;
    }

    if (moduleEnabled) {
      if (!reviewConfirmed) {
        setSubmitErr({
          kind: 'local',
          message: 'Confirmez la relecture avant de clôturer.',
        });
        return;
      }
      if (moduleCommentRequired && !varianceComment.trim()) {
        setSubmitErr({
          kind: 'local',
          message: `Un commentaire est obligatoire si l’écart dépasse ${CLOSE_VARIANCE_TOLERANCE_EUR.toFixed(2)} €.`,
        });
        return;
      }
    } else if (legacyCommentRequired && !varianceComment.trim()) {
      setSubmitErr({
        kind: 'local',
        message: `Un commentaire est obligatoire si l’écart dépasse ${CLOSE_VARIANCE_TOLERANCE_EUR.toFixed(2)} € par rapport au montant théorique.`,
      });
      return;
    }

    setSubmitErr(null);
    setBusy(true);
    try {
      const closeActual = moduleEnabled
        ? (denomCount?.total_counted_cents ?? liveTotalCents) / 100
        : actualNum;

      const res = await postCloseCashSession(
        session.id,
        {
          actual_amount: closeActual,
          variance_comment: varianceComment.trim() || null,
        },
        auth,
        { stepUpPin: pinTrim, contextBinding },
      );
      if (!res.ok) {
        const base = recycliqueClientFailureFromSalesHttp(res);
        const closeDetail = cashSessionCloseFailureMessage(res);
        const message =
          res.code === 'CASH_SESSION_CLOSE_HELD_PENDING'
            ? `${closeDetail} (finalisez ou abandonnez les tickets en attente.)`
            : closeDetail;
        setSubmitErr({
          kind: 'api',
          failure: { ...base, message, code: res.code ?? base.code },
        });
        return;
      }
      if (res.data.kind === 'deleted') {
        setDone({
          kind: 'deleted',
          message: res.data.message,
        });
        setSession(null);
        return;
      }
      setDone({
        kind: 'closed',
        sessionId: session.id,
        anomalyCloseSheet: res.data.anomaly_close_sheet,
        closeSheetPdfUrl: res.data.close_sheet_pdf_url,
      });
      setSession(null);
    } finally {
      setBusy(false);
    }
  };

  if (entry.blocked) {
    return (
      <Alert color="orange" title={entry.title} data-testid="cashflow-close-context-blocked">
        <Text size="sm">{entry.body}</Text>
      </Alert>
    );
  }

  if (loading || (moduleConfigLoading && !session)) {
    return (
      <Stack gap="xs" data-testid="cashflow-close-loading-wrap">
        <Button variant="subtle" size="xs" data-testid="cashflow-close-back-to-caisse" onClick={() => spaNavigateTo('/caisse')}>
          ← Retour au poste caisse
        </Button>
        <Text size="sm" data-testid="cashflow-close-loading">
          Chargement de la session courante…
        </Text>
      </Stack>
    );
  }

  if (loadErr) {
    return (
      <div data-testid="cashflow-close-load-error-wrap">
        <Button variant="subtle" size="xs" mb="sm" data-testid="cashflow-close-back-to-caisse" onClick={() => spaNavigateTo('/caisse')}>
          ← Retour au poste caisse
        </Button>
        <CashflowClientErrorAlert error={loadErr} testId="cashflow-close-load-error" />
        <Button mt="sm" size="xs" variant="light" onClick={() => void refreshSession()}>
          Réessayer
        </Button>
      </div>
    );
  }

  if (done) {
    return (
      <div className={classes.step} data-testid="cashflow-close-success">
        <Button variant="subtle" size="xs" mb="sm" data-testid="cashflow-close-back-to-caisse" onClick={() => spaNavigateTo('/caisse')}>
          ← Retour au poste caisse
        </Button>
        <Alert color="green" title={done.kind === 'deleted' ? 'Session vide non enregistrée' : 'Session fermée'}>
          <Text size="sm">
            {done.kind === 'deleted'
              ? done.message ??
                'La session ne contenait aucune transaction : elle a été supprimée côté serveur (pas de session fantôme fermée).'
              : 'La session est close dans Recyclique.'}
          </Text>
        </Alert>
        <div className={classes.relay} data-testid="cashflow-close-relay-epic8">
          {RELAY_EPIC8_COPY}
        </div>
        {done.kind === 'closed' && done.anomalyCloseSheet && done.closeSheetPdfUrl ? (
          <Button
            component="a"
            href={done.closeSheetPdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            size="sm"
            variant="light"
            mt="sm"
            data-testid="cashflow-close-pdf-anomaly"
          >
            Télécharger la feuille de clôture (anomalie)
          </Button>
        ) : null}
        {done.kind === 'closed' ? (
          <Stack gap="xs" mt="md" data-testid="cashflow-close-admin-relay">
            <Text size="sm" fw={600}>
              Supervision admin (prolongement exploitable)
            </Text>
            <Text size="xs" c="dimmed">
              Cible brownfield : gestionnaire de sessions (`/admin/session-manager`, entrée nav manifestée —{' '}
              <strong>Story 18.2</strong>) puis détail (`/admin/cash-sessions/:id`, <code>PageManifest</code>{' '}
              <code>admin-cash-session-detail</code>). Aucun état Paheko ni sync inventée ; parité complète visée en 6.10.
            </Text>
            <Group gap="sm">
              <Button size="xs" variant="light" onClick={() => spaNavigateTo('/admin')} data-testid="cashflow-close-admin-zone">
                Zone admin (démo)
              </Button>
              <Button
                size="xs"
                variant="default"
                data-testid="cashflow-close-admin-session-detail"
                onClick={() => {
                  const path = `/admin/cash-sessions/${done.sessionId}`;
                  const full =
                    typeof window !== 'undefined' ? `${window.location.origin}${path}` : path;
                  void navigator.clipboard?.writeText(full);
                }}
              >
                Copier le lien détail session (brownfield)
              </Button>
            </Group>
          </Stack>
        ) : (
          <Stack gap="xs" mt="md" data-testid="cashflow-close-admin-relay-deleted">
            <Text size="xs" c="dimmed">
              Pour la supervision des sessions côté admin, utilisez le gestionnaire de sessions lorsqu’il est servi (6.10).
            </Text>
            <Button size="xs" variant="light" onClick={() => spaNavigateTo('/admin')} data-testid="cashflow-close-admin-zone">
              Zone admin (démo)
            </Button>
          </Stack>
        )}
        <Button
          size="sm"
          variant="light"
          mt="sm"
          onClick={() => {
            setDone(null);
            setPin('');
            setVarianceComment('');
            setReviewConfirmed(false);
            setMaxAccessibleTab(0);
            setDenomCount(null);
            setTab(0);
            void refreshSession();
          }}
        >
          Fermer
        </Button>
      </div>
    );
  }

  if (!session) {
    return (
      <Stack gap="xs" data-testid="cashflow-close-no-session-wrap">
        <Button variant="subtle" size="xs" data-testid="cashflow-close-back-to-caisse" onClick={() => spaNavigateTo('/caisse')}>
          ← Retour au poste caisse
        </Button>
        <Alert color="blue" title="Aucune session ouverte" data-testid="cashflow-close-no-session">
          <Text size="sm">
            Le serveur ne signale aucune session de caisse ouverte pour votre compte. Ouvrez une session depuis le flux
            caisse habituel avant de clôturer.
          </Text>
        </Alert>
      </Stack>
    );
  }

  const totals = session.totals;

  const recapPanel = {
    id: 'recap',
    title: '1. Récap',
    content: (
      <div className={classes.step}>
        <Text size="sm" fw={600}>
          Contrôles avant clôture (données serveur)
        </Text>
        <div className={classes.recapGrid} data-testid="cashflow-close-recap">
          <span className={classes.recapLabel}>Montant initial</span>
          <span>{fmtEur(session.initial_amount)}</span>
          <span className={classes.recapLabel}>Total ventes (session)</span>
          <span>{fmtEur(session.total_sales ?? 0)}</span>
          <span className={classes.recapLabel}>Total dons</span>
          <span>{fmtEur(session.total_donations ?? 0)}</span>
          <span className={classes.recapLabel}>Poids sortant (kg)</span>
          <span>{session.total_weight_out != null ? String(session.total_weight_out) : '—'}</span>
          {totals ? (
            <>
              <span className={classes.recapLabel}>Ventes complétées</span>
              <span>{fmtEur(totals.sales_completed)}</span>
              <span className={classes.recapLabel}>Remboursements (algébrique)</span>
              <span>{fmtEur(totals.refunds)}</span>
              <span className={classes.recapLabel}>Net (6.4)</span>
              <span>{fmtEur(totals.net)}</span>
            </>
          ) : null}
          <span className={classes.recapLabel}>Montant théorique caisse</span>
          <span data-testid="cashflow-close-theoretical">{fmtEur(theoretical)}</span>
        </div>
        <Button size="sm" onClick={() => navigateToTab(1, { bumpMaxTo: 1 })}>
          {moduleEnabled ? 'Continuer vers le comptage grille' : 'Continuer vers le comptage'}
        </Button>
      </div>
    ),
  };

  const legacyAmountPanel = {
    id: 'amounts',
    title: '2. Comptage',
    content: (
      <div className={classes.step}>
        <Text size="sm">Saisissez le montant physique compté en caisse.</Text>
        <NumberInput
          label="Montant compté (€)"
          min={0}
          decimalScale={2}
          fixedDecimalScale
          value={actualAmount}
          onChange={setActualAmount}
          data-testid="cashflow-close-actual-amount"
        />
        {legacyCommentRequired ? (
          <TextInput
            label="Commentaire d’écart (obligatoire)"
            description={`Écart supérieur à ${CLOSE_VARIANCE_TOLERANCE_EUR.toFixed(2)} € par rapport au théorique (${fmtEur(theoretical)}).`}
            value={varianceComment}
            onChange={(e) => setVarianceComment(e.currentTarget.value)}
            data-testid="cashflow-close-variance-comment"
          />
        ) : null}
        <Button size="sm" variant="default" onClick={() => setTab(0)}>
          Retour
        </Button>
        <Button size="sm" onClick={() => setTab(2)}>
          Continuer vers le PIN
        </Button>
      </div>
    ),
  };

  const pinPanelLegacy = {
    id: 'pin',
    title: '3. Confirmer',
    content: (
      <div className={classes.step}>
        <Text size="sm">
          La clôture exige le PIN métier (preuve step-up). Il n’est pas journalisé côté client.
        </Text>
        <PasswordInput
          label="PIN step-up"
          type="password"
          autoComplete="off"
          value={pin}
          onChange={(e) => setPin(e.currentTarget.value)}
          data-testid="cashflow-close-pin"
        />
        <CashflowClientErrorAlert error={submitErr} testId="cashflow-close-submit-error" />
        <Button size="sm" variant="default" onClick={() => setTab(1)} disabled={busy}>
          Retour
        </Button>
        <Button
          size="sm"
          loading={busy}
          onClick={() => void onSubmitClose()}
          data-testid="cashflow-close-submit"
          disabled={stale}
        >
          Clôturer la session
        </Button>
      </div>
    ),
  };

  const modulePanels = moduleEnabled
    ? [
        recapPanel,
        {
          id: 'denomination-grid',
          title: '2. Grille',
          content: (
            <>
              <CashflowClientErrorAlert error={gridErr} testId="cashflow-denomination-grid-error" />
              <CashflowDenominationGridPanel
                denominations={denominations}
                quantities={quantities}
                onQuantityChange={onQuantityChange}
                showImages={comptageConfig.show_images}
                liveTotalCents={liveTotalCents}
                serverTotalCents={denomCount?.total_counted_cents ?? null}
                onBack={() => navigateToTab(0)}
                onContinue={() => void onGridContinue()}
                busy={gridBusy}
              />
            </>
          ),
        },
        {
          id: 'verify',
          title: '3. Vérifier',
          content: denomCount ? (
            <CashflowCloseVerifyPanel
              denomCount={denomCount}
              onBack={() => navigateToTab(1)}
              onContinue={() => navigateToTab(3, { bumpMaxTo: 3 })}
            />
          ) : (
            <Text size="sm">Chargement des totaux serveur…</Text>
          ),
        },
        {
          id: 'variance',
          title: '4. Écart',
          content: (
            <div className={classes.step} data-testid="cashflow-close-variance-step">
              {moduleCommentRequired ? (
                <>
                  <Text size="sm">
                    Un écart a été détecté — commentaire obligatoire avant la relecture.
                  </Text>
                  <TextInput
                    label="Commentaire d’écart (obligatoire)"
                    description={
                      denomCount
                        ? `Écart ${fmtEur(denomCount.variance_cents / 100)} — tolérance ${CLOSE_VARIANCE_TOLERANCE_EUR.toFixed(2)} €.`
                        : undefined
                    }
                    value={varianceComment}
                    onChange={(e) => setVarianceComment(e.currentTarget.value)}
                    data-testid="cashflow-close-variance-comment"
                  />
                </>
              ) : (
                <Text size="sm">Aucun écart significatif — vous pouvez continuer vers la relecture.</Text>
              )}
              <Button size="sm" variant="default" onClick={() => navigateToTab(2)}>
                Retour
              </Button>
              <Button
                size="sm"
                onClick={() => {
                  if (moduleCommentRequired && !varianceComment.trim()) return;
                  navigateToTab(4, { bumpMaxTo: 4 });
                }}
                disabled={moduleCommentRequired && !varianceComment.trim()}
                data-testid="cashflow-close-variance-continue"
              >
                Continuer vers la relecture
              </Button>
            </div>
          ),
        },
        {
          id: 'review',
          title: '5. Relecture',
          content: denomCount ? (
            <CashflowCloseReviewPanel
              denomCount={denomCount}
              onConfirmReview={() => {
                setReviewConfirmed(true);
                navigateToTab(5, { bumpMaxTo: 5 });
              }}
              onBack={() => navigateToTab(3)}
              reviewConfirmed={reviewConfirmed}
            />
          ) : (
            <Text size="sm">Données de relecture indisponibles.</Text>
          ),
        },
        {
          id: 'pin',
          title: '6. Confirmer',
          content: (
            <div className={classes.step}>
              <Text size="sm">
                La clôture exige le PIN métier (preuve step-up). Le total de la grille sera enregistré comme montant
                compté.
              </Text>
              {denomCount &&
              (varianceExceedsD33Threshold(denomCount.variance_cents) ||
                hasRare500EuroNote(denomCount)) ? (
                <Alert color="orange" title="Attention clôture" data-testid="cashflow-close-pin-alert">
                  <Text size="sm">
                    {varianceExceedsD33Threshold(denomCount.variance_cents)
                      ? `L'écart dépasse le seuil site (${DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR.toFixed(2)} €) — vérifiez le commentaire avant de confirmer.`
                      : null}
                    {varianceExceedsD33Threshold(denomCount.variance_cents) &&
                    hasRare500EuroNote(denomCount)
                      ? ' '
                      : null}
                    {hasRare500EuroNote(denomCount)
                      ? 'Une coupure rare (500 €) est présente dans le comptage — vérifiez avant de confirmer.'
                      : null}
                  </Text>
                </Alert>
              ) : null}
              <PasswordInput
                label="PIN step-up"
                type="password"
                autoComplete="off"
                value={pin}
                onChange={(e) => setPin(e.currentTarget.value)}
                data-testid="cashflow-close-pin"
              />
              <CashflowClientErrorAlert error={submitErr} testId="cashflow-close-submit-error" />
              <Button
                size="sm"
                variant="default"
                onClick={() => navigateToTab(4)}
                disabled={busy}
              >
                Retour
              </Button>
              <Button
                size="sm"
                loading={busy}
                onClick={() => void onSubmitClose()}
                data-testid="cashflow-close-submit"
                disabled={stale || !reviewConfirmed}
              >
                Clôturer la session
              </Button>
            </div>
          ),
        },
      ]
    : [recapPanel, legacyAmountPanel, pinPanelLegacy];

  return (
    <div data-testid="cashflow-close-wizard">
      <Button variant="subtle" size="xs" mb="sm" data-testid="cashflow-close-back-to-caisse" onClick={() => spaNavigateTo('/caisse')}>
        ← Retour au poste caisse
      </Button>
      <CashflowOperationalSyncNotice auth={auth} />
      {stale ? (
        <Alert color="orange" title="Données ticket / contexte périmées" mb="sm" data-testid="cashflow-close-stale-block">
          <Text size="sm">
            Le widget ticket critique est en DATA_STALE — la clôture est bloquée jusqu’à retour NOMINAL (GET ticket ou
            rafraîchissement).
          </Text>
        </Alert>
      ) : null}
      <FlowRenderer
        flowId="cashflow-close"
        panels={modulePanels}
        activeIndex={tab}
        onActiveIndexChange={navigateToTab}
        isTabDisabled={moduleEnabled ? isModuleTabDisabled : undefined}
        keepMounted
      />
    </div>
  );
}
