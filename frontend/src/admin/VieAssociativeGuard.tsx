/**
 * Garde vie associative — Story 8.7.
 * Accès si l'utilisateur a la permission admin ou vie_asso.access.
 */
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

const VIE_ASSO_PERMISSIONS = ['admin', 'vie_asso.access'];

export function VieAssociativeGuard({ children }: { children: React.ReactNode }) {
  const { permissions, user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  const hasAccess = VIE_ASSO_PERMISSIONS.some((p) => permissions.includes(p));
  if (!hasAccess) {
    return (
      <div data-testid="vie-associative-forbidden">
        <p>Accès réservé (vie associative ou administrateur).</p>
      </div>
    );
  }
  return <>{children}</>;
}
