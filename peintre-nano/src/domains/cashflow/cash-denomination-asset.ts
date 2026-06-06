import type { CashDenominationV1 } from '../../api/cash-session-client';

/** Chemin public stable : `peintre-nano/public/assets/cash-denominations/{code}.svg`. */
export function cashDenominationAssetUrl(code: string): string {
  return `/assets/cash-denominations/${code}.svg`;
}

export function sortDenominationsForGrid(
  denominations: readonly CashDenominationV1[],
): CashDenominationV1[] {
  return [...denominations].sort((a, b) => a.display_order - b.display_order);
}

export function splitMainAndRareDenominations(denominations: readonly CashDenominationV1[]): {
  main: CashDenominationV1[];
  rare: CashDenominationV1[];
} {
  const sorted = sortDenominationsForGrid(denominations);
  const main: CashDenominationV1[] = [];
  const rare: CashDenominationV1[] = [];
  for (const d of sorted) {
    if (d.code === 'EUR_50000') {
      rare.push(d);
    } else {
      main.push(d);
    }
  }
  return { main, rare };
}
