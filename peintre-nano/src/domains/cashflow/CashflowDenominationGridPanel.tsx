import { ActionIcon, Button, Collapse, Group, NumberInput, Stack, Text, UnstyledButton } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { Minus, Plus, RotateCcw } from 'lucide-react';
import { useMemo, type ReactNode } from 'react';
import type { CashDenominationV1 } from '../../api/cash-session-client';
import { cashDenominationAssetUrl, splitMainAndRareDenominations } from './cash-denomination-asset';
import { CashflowDenominationRulesBanner } from './CashflowDenominationRulesBanner';
import classes from './CashflowCloseWizard.module.css';

export type CashflowDenominationGridPanelProps = {
  readonly denominations: readonly CashDenominationV1[];
  readonly quantities: Readonly<Record<string, number>>;
  readonly onQuantityChange: (code: string, quantity: number) => void;
  readonly showImages: boolean;
  readonly liveTotalCents: number;
  readonly serverTotalCents: number | null;
  readonly onBack: () => void;
  readonly onContinue: () => void;
  readonly busy?: boolean;
};

function fmtEurFromCents(cents: number): string {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(cents / 100);
}

function DenominationRow({
  denom,
  quantity,
  showImages,
  onQuantityChange,
}: {
  readonly denom: CashDenominationV1;
  readonly quantity: number;
  readonly showImages: boolean;
  readonly onQuantityChange: (code: string, quantity: number) => void;
}): ReactNode {
  const isOneEuro = denom.code === 'EUR_100';
  const isTwoEuro = denom.code === 'EUR_200';
  const rowClass = [
    classes.denomRow,
    isOneEuro ? classes.denomRowOneEuro : '',
    isTwoEuro ? classes.denomRowTwoEuro : '',
  ]
    .filter(Boolean)
    .join(' ');

  const setQty = (next: number) => onQuantityChange(denom.code, Math.max(0, Math.floor(next)));

  return (
    <div className={rowClass} data-testid={`cashflow-denom-row-${denom.code}`}>
      <Group gap="sm" wrap="nowrap" className={classes.denomLabelGroup}>
        {showImages ? (
          <img
            src={cashDenominationAssetUrl(denom.code)}
            alt=""
            width={40}
            height={40}
            className={classes.denomPicto}
            data-testid={`cashflow-denom-picto-${denom.code}`}
          />
        ) : null}
        <Text size="sm" fw={600}>
          {denom.label_fr}
        </Text>
      </Group>
      <Group gap={4} wrap="nowrap" className={classes.denomControls}>
        <ActionIcon
          variant="default"
          size="lg"
          aria-label={`Diminuer ${denom.label_fr}`}
          onClick={() => setQty(quantity - 1)}
          className={classes.denomStepper}
          data-testid={`cashflow-denom-minus-${denom.code}`}
        >
          <Minus size={18} />
        </ActionIcon>
        <NumberInput
          value={quantity}
          min={0}
          max={9999}
          hideControls
          allowDecimal={false}
          onChange={(v) => setQty(typeof v === 'number' ? v : parseInt(String(v), 10) || 0)}
          classNames={{ input: classes.denomQtyInput }}
          data-testid={`cashflow-denom-qty-${denom.code}`}
        />
        <ActionIcon
          variant="default"
          size="lg"
          aria-label={`Augmenter ${denom.label_fr}`}
          onClick={() => setQty(quantity + 1)}
          className={classes.denomStepper}
          data-testid={`cashflow-denom-plus-${denom.code}`}
        >
          <Plus size={18} />
        </ActionIcon>
        <UnstyledButton
          className={classes.denomReset}
          onClick={() => setQty(0)}
          aria-label={`Remettre à zéro ${denom.label_fr}`}
          data-testid={`cashflow-denom-reset-${denom.code}`}
        >
          <RotateCcw size={16} />
        </UnstyledButton>
      </Group>
    </div>
  );
}

/** Story 9.12 — grille hybride pièces/billets avec section « Coupures rares » (500 € seul). */
export function CashflowDenominationGridPanel({
  denominations,
  quantities,
  onQuantityChange,
  showImages,
  liveTotalCents,
  serverTotalCents,
  onBack,
  onContinue,
  busy = false,
}: CashflowDenominationGridPanelProps): ReactNode {
  const { main, rare } = useMemo(() => splitMainAndRareDenominations(denominations), [denominations]);
  const [rareOpen, { toggle: toggleRare }] = useDisclosure(false);

  return (
    <div className={classes.step} data-testid="cashflow-denomination-grid">
      <CashflowDenominationRulesBanner />
      <Text size="sm">Comptez chaque coupure du tiroir (quantités, pas de montant global).</Text>

      <Stack gap="xs" className={classes.denomGridMain} data-testid="cashflow-denomination-grid-main">
        {main.map((d) => (
          <DenominationRow
            key={d.code}
            denom={d}
            quantity={quantities[d.code] ?? 0}
            showImages={showImages}
            onQuantityChange={onQuantityChange}
          />
        ))}
      </Stack>

      {rare.length > 0 ? (
        <div data-testid="cashflow-denomination-rares">
          <Button variant="subtle" size="xs" onClick={toggleRare} data-testid="cashflow-denomination-rares-toggle">
            Coupures rares {rareOpen ? '▲' : '▼'}
          </Button>
          <Collapse in={rareOpen}>
            <Stack gap="xs" mt="xs" className={classes.denomGridRare}>
              {rare.map((d) => (
                <DenominationRow
                  key={d.code}
                  denom={d}
                  quantity={quantities[d.code] ?? 0}
                  showImages={showImages}
                  onQuantityChange={onQuantityChange}
                />
              ))}
            </Stack>
          </Collapse>
        </div>
      ) : null}

      <div className={classes.denomTotalLive} data-testid="cashflow-denomination-total">
        <Text size="sm" fw={600}>
          Total compté (grille) : {fmtEurFromCents(liveTotalCents)}
        </Text>
        {serverTotalCents != null && serverTotalCents !== liveTotalCents ? (
          <Text size="xs" c="dimmed">
            Serveur : {fmtEurFromCents(serverTotalCents)} (réconciliation en cours)
          </Text>
        ) : null}
      </div>

      <Group gap="sm">
        <Button size="sm" variant="default" onClick={onBack} disabled={busy}>
          Retour
        </Button>
        <Button size="sm" onClick={onContinue} loading={busy} data-testid="cashflow-denomination-continue">
          Continuer vers la vérification
        </Button>
      </Group>
    </div>
  );
}
