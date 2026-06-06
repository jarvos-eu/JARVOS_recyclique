import { Alert, Button, Group, Text } from '@mantine/core';
import type { ReactNode } from 'react';
import type { DenominationCountResponseV1 } from '../../api/cash-session-client';
import classes from './CashflowCloseWizard.module.css';

export type CashflowCloseReviewPanelProps = {
  readonly denomCount: DenominationCountResponseV1;
  readonly operatorLabel?: string | null;
  readonly onConfirmReview: () => void;
  readonly onBack: () => void;
  readonly reviewConfirmed: boolean;
};

function fmtEurFromCents(cents: number): string {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(cents / 100);
}

/** Story 9.12 D-CPT-05 — relecture obligatoire avant PIN, non skippable. */
export function CashflowCloseReviewPanel({
  denomCount,
  operatorLabel,
  onConfirmReview,
  onBack,
  reviewConfirmed,
}: CashflowCloseReviewPanelProps): ReactNode {
  const recordedAt = denomCount.recorded_at
    ? new Intl.DateTimeFormat('fr-FR', { dateStyle: 'short', timeStyle: 'short' }).format(
        new Date(denomCount.recorded_at),
      )
    : '—';

  return (
    <div className={classes.step} data-testid="cashflow-close-review">
      <Text size="sm" fw={600}>
        Relecture avant validation
      </Text>
      <Alert color="yellow" variant="light">
        <Text size="sm">
          Vérifiez une dernière fois : <strong>le total de la grille fera foi</strong> à la clôture.
        </Text>
      </Alert>
      <div className={classes.recapGrid}>
        <span className={classes.recapLabel}>Clôturant</span>
        <span>{operatorLabel?.trim() || 'Opérateur courant'}</span>
        <span className={classes.recapLabel}>Heure comptage</span>
        <span>{recordedAt}</span>
        <span className={classes.recapLabel}>Total grille</span>
        <span data-testid="cashflow-review-total">{fmtEurFromCents(denomCount.total_counted_cents)}</span>
        <span className={classes.recapLabel}>Écart</span>
        <span>{fmtEurFromCents(denomCount.variance_cents)}</span>
      </div>
      <Group gap="sm">
        <Button size="sm" variant="default" onClick={onBack}>
          Retour
        </Button>
        <Button
          size="sm"
          onClick={onConfirmReview}
          disabled={reviewConfirmed}
          data-testid="cashflow-close-review-confirm"
        >
          {reviewConfirmed ? 'Relecture confirmée' : 'J’ai relu'}
        </Button>
      </Group>
    </div>
  );
}
