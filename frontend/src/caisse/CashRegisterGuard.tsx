/**
 * Garde de routes — Story 3.5.
 * En mode caisse verrouillé, redirige vers /caisse ou /cash-register/pin
 * toute tentative d'accès à une route non caisse.
 * À utiliser avec React Router (useLocation, useNavigate).
 */
import { useEffect, type ReactNode } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CAISSE_DEFAULT_REDIRECT } from './cashRegisterRoutes';
import { useCashRegisterLock } from './useCashRegisterLock';

export interface CashRegisterGuardProps {
  children: ReactNode;
  /** Redirection si accès refusé (défaut: /caisse). */
  redirectTo?: string;
}

/**
 * Wrapper qui redirige vers l'écran caisse (ou PIN) lorsque l'utilisateur
 * en mode verrouillé tente d'accéder à une route non autorisée.
 */
export function CashRegisterGuard({ children, redirectTo = CAISSE_DEFAULT_REDIRECT }: CashRegisterGuardProps) {
  const { isRestricted, isPathAllowed } = useCashRegisterLock();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isRestricted) return;
    const pathname = location.pathname;
    if (!isPathAllowed(pathname)) {
      navigate(redirectTo, { replace: true });
    }
  }, [isRestricted, location.pathname, isPathAllowed, navigate, redirectTo]);

  return <>{children}</>;
}
