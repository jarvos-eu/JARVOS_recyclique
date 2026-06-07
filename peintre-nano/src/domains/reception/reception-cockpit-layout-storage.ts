/** Story 28.3 — ratios colonnes cockpit (legacy LAYOUT_STORAGE_KEY, version Peintre). */
export const RECEPTION_COCKPIT_LAYOUT_STORAGE_KEY = 'reception-cockpit-layout-v1';

export type ReceptionCockpitLayoutRatios = {
  readonly leftPct: number;
  readonly centerPct: number;
};

export const DEFAULT_RECEPTION_COCKPIT_LAYOUT: ReceptionCockpitLayoutRatios = {
  leftPct: 28,
  centerPct: 48,
};

const MIN_COLUMN_PCT = 18;
const MAX_COLUMN_PCT = 64;

export function rightColumnPct(layout: ReceptionCockpitLayoutRatios): number {
  return 100 - layout.leftPct - layout.centerPct;
}

export function clampReceptionCockpitLayout(
  leftPct: number,
  centerPct: number,
): ReceptionCockpitLayoutRatios {
  let left = Math.round(leftPct);
  let center = Math.round(centerPct);
  left = Math.min(MAX_COLUMN_PCT, Math.max(MIN_COLUMN_PCT, left));
  center = Math.min(MAX_COLUMN_PCT, Math.max(MIN_COLUMN_PCT, center));
  let right = 100 - left - center;
  if (right < MIN_COLUMN_PCT) {
    center = Math.max(MIN_COLUMN_PCT, center - (MIN_COLUMN_PCT - right));
    right = 100 - left - center;
  }
  if (right < MIN_COLUMN_PCT) {
    left = Math.max(MIN_COLUMN_PCT, left - (MIN_COLUMN_PCT - right));
  }
  return { leftPct: left, centerPct: center };
}

function parseStoredLayout(raw: string | null): ReceptionCockpitLayoutRatios | null {
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as { leftPct?: unknown; centerPct?: unknown };
    if (typeof parsed.leftPct !== 'number' || typeof parsed.centerPct !== 'number') return null;
    return clampReceptionCockpitLayout(parsed.leftPct, parsed.centerPct);
  } catch {
    return null;
  }
}

export function loadReceptionCockpitLayout(): ReceptionCockpitLayoutRatios {
  if (typeof window === 'undefined') return DEFAULT_RECEPTION_COCKPIT_LAYOUT;
  const stored = parseStoredLayout(window.localStorage.getItem(RECEPTION_COCKPIT_LAYOUT_STORAGE_KEY));
  return stored ?? DEFAULT_RECEPTION_COCKPIT_LAYOUT;
}

export function saveReceptionCockpitLayout(layout: ReceptionCockpitLayoutRatios): void {
  if (typeof window === 'undefined') return;
  const clamped = clampReceptionCockpitLayout(layout.leftPct, layout.centerPct);
  try {
    window.localStorage.setItem(RECEPTION_COCKPIT_LAYOUT_STORAGE_KEY, JSON.stringify(clamped));
  } catch {
    // quota dépassé ou mode privé — ignorer
  }
}

export function buildCockpitGridTemplateColumns(layout: ReceptionCockpitLayoutRatios): string {
  const right = rightColumnPct(layout);
  return `minmax(20rem, ${layout.leftPct}fr) 6px minmax(24rem, ${layout.centerPct}fr) 6px minmax(16rem, ${right}fr)`;
}
