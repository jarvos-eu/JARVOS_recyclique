/**
 * Contexte auth minimal — Story 3.3, 3.5, 11.1.
 * Expose setFromPinLogin, login, logout et accessToken pour les appels API.
 */
import React, { createContext, useCallback, useContext, useState } from 'react';
import type { UserInToken } from '../api/auth';
import { postLogin, postLogout } from '../api/auth';

export interface AuthState {
  user: UserInToken | null;
  accessToken: string | null;
  refreshToken: string | null;
  permissions: string[];
}

interface AuthContextValue extends AuthState {
  setFromPinLogin: (user: UserInToken, accessToken: string, refreshToken: string, permissions?: string[]) => void;
  setTokens: (accessToken: string | null, refreshToken: string | null) => void;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
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

  const login = useCallback(async (username: string, password: string) => {
    const data = await postLogin(username, password);
    setState({
      user: data.user,
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
      permissions: data.permissions ?? [],
    });
  }, []);

  const logout = useCallback(async () => {
    if (state.refreshToken) {
      try {
        await postLogout(state.refreshToken);
      } catch {
        // ignore
      }
    }
    setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      permissions: [],
    });
  }, [state.refreshToken]);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        setFromPinLogin,
        setTokens,
        login,
        logout,
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
