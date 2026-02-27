/**
 * Contexte auth minimal — Story 3.3, 3.5.
 * Expose setFromPinLogin pour le déverrouillage PIN et accessToken pour les appels API (ex. getCashRegistersStatus).
 * À étendre (login classique, refresh) dans les stories auth dédiées.
 */
import React, { createContext, useCallback, useContext, useState } from 'react';
import type { UserInToken } from '../api/auth';

export interface AuthState {
  user: UserInToken | null;
  accessToken: string | null;
  refreshToken: string | null;
  permissions: string[];
}

interface AuthContextValue extends AuthState {
  setFromPinLogin: (user: UserInToken, accessToken: string, refreshToken: string, permissions?: string[]) => void;
  setTokens: (accessToken: string | null, refreshToken: string | null) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    accessToken: null,
    refreshToken: null,
    permissions: [],
  });

  const setFromPinLogin = useCallback(
    (user: UserInToken, accessToken: string, refreshToken: string, permissions?: string[]) => {
      setState({ user, accessToken, refreshToken, permissions: permissions ?? [] });
    },
    []
  );

  const setTokens = useCallback((accessToken: string | null, refreshToken: string | null) => {
    setState((s) => ({ ...s, accessToken, refreshToken }));
  }, []);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        setFromPinLogin,
        setTokens,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
