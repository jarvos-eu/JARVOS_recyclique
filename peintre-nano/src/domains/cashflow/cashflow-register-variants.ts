import type { CashRegisterStatusRowV1 } from '../../api/cash-session-client';

/** Parité legacy `CashRegisterDashboard.getFirstVirtualRegister` — poste dédié simulation. */
export function firstVirtualRegisterId(rows: readonly CashRegisterStatusRowV1[]): string | null {
  const row = rows.find((r) => r.enable_virtual === true && r.id.trim().length > 0);
  return row?.id.trim() ?? null;
}

/** Parité legacy `CashRegisterDashboard.getFirstDeferredRegister`. */
export function firstDeferredRegisterId(rows: readonly CashRegisterStatusRowV1[]): string | null {
  const row = rows.find((r) => r.enable_deferred === true && r.id.trim().length > 0);
  return row?.id.trim() ?? null;
}

export function formatCashSessionOpenedAt(iso: string | undefined | null): string | null {
  const raw = iso?.trim();
  if (!raw) return null;
  const d = new Date(raw);
  if (Number.isNaN(d.getTime())) return null;
  return new Intl.DateTimeFormat('fr-FR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(d);
}
