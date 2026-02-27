/**
 * Garde admin — Story 8.1.
 * Redirige si l'utilisateur n'a pas la permission admin.
 */
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export function AdminGuard({ children }: { children: React.ReactNode }) {
  const { permissions, user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (!permissions.includes('admin')) {
    return (
      <div data-testid="admin-forbidden">
        <p>Accès réservé aux administrateurs.</p>
      </div>
    );
  }
  return <>{children}</>;
}
