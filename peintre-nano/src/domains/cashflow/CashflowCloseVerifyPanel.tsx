import { Button, Group, Text } from '@mantine/core';
import type { ReactNode } from 'react';
import type { DenominationCountResponseV1 } from '../../api/cash-session-client';
import classes from './CashflowCloseWizard.module.css';

export type CashflowCloseVerifyPanelProps = {
  readonly denomCount: DenominationCountResponseV1;
  readonly onBack: () => void;
  readonly onContinue: () => void;
};

function fmtEurFromCents(cents: number): string {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(cents / 100);
}

/** Story 9.12 — théorique / compté / écart / fond cible / retrait (valeurs serveur uniquement). */
export function CashflowCloseVerifyPanel({
  denomCount,
  onBack,
  onContinue,
}: CashflowCloseVerifyPanelProps): ReactNode {
  const variance = denomCount.variance_cents;

  return (
    <div className={classes.step} data-testid="cashflow-close-verify">
      <Text size="sm" fw={600}>
        Vérification (données serveur)
      </Text>
      <div className={classes.recapGrid}>
        <span className={classes.recapLabel}>Montant théorique espèces</span>
        <span data-testid="cashflow-verify-theoretical">
          {fmtEurFromCents(denomCount.theoretical_cash_cents)}
        </span>
        <span className={classes.recapLabel}>Total compté (grille)</span>
        <span data-testid="cashflow-verify-counted">{fmtEurFromCents(denomCount.total_counted_cents)}</span>
        <span className={classes.recapLabel}>Écart</span>
        <span data-testid="cashflow-verify-variance">{fmtEurFromCents(variance)}</span>
        <span className={classes.recapLabel}>Fond cible à laisser</span>
        <span data-testid="cashflow-verify-float-target">{fmtEurFromCents(denomCount.float_target_cents)}</span>
        <span className={classes.recapLabel}>Montant à retirer</span>
        <span data-testid="cashflow-verify-withdraw">{fmtEurFromCents(denomCount.withdraw_cents)}</span>
      </div>
      <Group gap="sm">
        <Button size="sm" variant="default" onClick={onBack}>
          Retour
        </Button>
        <Button size="sm" onClick={onContinue} data-testid="cashflow-verify-continue">
          Continuer
        </Button>
      </Group>
    </div>
  );
}
