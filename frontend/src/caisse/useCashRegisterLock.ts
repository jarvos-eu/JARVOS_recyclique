/**
 * Hook mode caisse verrouillé — Story 3.5.
 * Expose l'état « poste actif + verrouillé » pour garde de routes et menu.
 */
import { useCaisse } from './CaisseContext';
import { isCaisseAllowedPath } from './cashRegisterRoutes';

export interface UseCashRegisterLockResult {
  /** Poste caisse démarré sélectionné. */
  isCashRegisterActive: boolean;
  /** Session non déverrouillée par PIN. */
  isLocked: boolean;
  /** Restriction active : seul le menu caisse est autorisé. */
  isRestricted: boolean;
  /** true si le pathname est autorisé en mode verrouillé. */
  isPathAllowed: (pathname: string) => boolean;
}

/**
 * Lit le contexte caisse et dérive la restriction (poste actif + verrouillé).
 * À utiliser dans le garde de routes et le composant menu.
 */
export function useCashRegisterLock(): UseCashRegisterLockResult {
  const { isCashRegisterActive, isLocked } = useCaisse();
  const isRestricted = isCashRegisterActive && isLocked;
  return {
    isCashRegisterActive,
    isLocked,
    isRestricted,
    isPathAllowed: isCaisseAllowedPath,
  };
}
