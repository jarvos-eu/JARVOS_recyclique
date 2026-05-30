// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { LiveAuthShell } from '../../src/app/auth/LiveAuthShell';

const { postRecycliqueLogin, fetchRecycliqueContextEnvelope, postRecycliqueLogout } = vi.hoisted(() => ({
  postRecycliqueLogin: vi.fn(),
  fetchRecycliqueContextEnvelope: vi.fn(),
  postRecycliqueLogout: vi.fn(),
}));

vi.mock('../../src/api/recyclique-auth-client', () => ({
  postRecycliqueLogin,
  fetchRecycliqueContextEnvelope,
  postRecycliqueLogout,
  LIVE_AUTH_ACCESS_TOKEN_STORAGE_KEY: 'peintre-nano.recyclique.access_token',
  LIVE_AUTH_USER_DISPLAY_KEY: 'peintre-nano.recyclique.user_display',
  persistUserDisplay: vi.fn(),
  readStoredUserDisplay: vi.fn(() => undefined),
}));

const { hasDeviceIdentity } = vi.hoisted(() => ({
  hasDeviceIdentity: vi.fn(async () => false),
}));

const { fetchOperatorSessionStatus } = vi.hoisted(() => ({
  fetchOperatorSessionStatus: vi.fn(async () => ({
    ok: true as const,
    active: true,
    operator_user_id: 'u-op',
    session_id: 'sess-1',
    last_activity_at: null,
    inactivity_timeout_seconds: null,
    seconds_until_lock: null,
  })),
}));

vi.mock('../../src/domains/shared-workstation/device-identity-store', () => ({
  hasDeviceIdentity,
  loadDeviceIdentity: vi.fn(async () => null),
  sharedWorkstationAuthHeaders: vi.fn(async () => ({})),
  hadPriorDeviceEnrollment: vi.fn(async () => false),
  saveDeviceIdentity: vi.fn(async () => undefined),
  clearDeviceIdentity: vi.fn(async () => undefined),
}));

vi.mock('../../src/api/shared-workstation-operator-session-client', () => ({
  fetchOperatorSessionStatus,
  fetchSharedWorkstationDeviceStatus: vi.fn(async () => ({
    ok: true as const,
    device_id: 'dev-1',
    inactivity_timeout_seconds: 600,
  })),
  endOperatorSession: vi.fn(async () => ({ ok: true as const, ended: true, session_id: 'sess-1' })),
  touchOperatorSessionActivity: vi.fn(async () => ({ ok: true as const, throttled: false })),
}));

vi.mock('../../src/api/shared-workstation-operator-pin-client', () => ({
  verifySharedWorkstationOperatorPin: vi.fn(),
}));

import '../../src/registry';

beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    configurable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }),
  });
});

afterEach(() => {
  cleanup();
  sessionStorage.clear();
  vi.clearAllMocks();
  window.history.pushState({}, '', '/');
});

describe('LiveAuthShell (Story 11.2)', () => {
  beforeEach(() => {
    sessionStorage.clear();
    window.history.pushState({}, '', '/login');
    hasDeviceIdentity.mockResolvedValue(false);
    fetchOperatorSessionStatus.mockResolvedValue({
      ok: true,
      active: true,
      operator_user_id: 'u-op',
      session_id: 'sess-1',
      last_activity_at: null,
      inactivity_timeout_seconds: null,
      seconds_until_lock: null,
    });
    postRecycliqueLogin.mockResolvedValue({
      ok: true,
      accessToken: 'test-token',
      refreshToken: null,
      userId: 'u1',
      userDisplayLabel: undefined,
    });
    fetchRecycliqueContextEnvelope.mockResolvedValue({
      ok: true,
      envelope: createDefaultDemoEnvelope(),
    });
  });

  it('après login réussi, l’URL est /dashboard (canon CREOS transverse-dashboard)', async () => {
    render(
      <MantineProvider>
        <LiveAuthShell>
          <span data-testid="post-login-child">in</span>
        </LiveAuthShell>
      </MantineProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('live-auth-public-shell')).toBeTruthy();
    });

    fireEvent.change(screen.getByRole('textbox', { name: /Nom d'utilisateur/ }), {
      target: { value: 'admin' },
    });
    fireEvent.change(screen.getByLabelText(/Mot de passe/), {
      target: { value: 'secret' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Se connecter' }));

    await waitFor(() => {
      expect(screen.getByTestId('post-login-child')).toBeTruthy();
    });
    expect(window.location.pathname).toBe('/dashboard');
    expect(screen.queryByTestId('live-auth-toolbar')).toBeNull();
    expect(screen.queryByText(/GET \/v1\/users\/me\/context/)).toBeNull();
    expect(screen.queryByText(/Auth live/)).toBeNull();
  });

  it('restauration de session sur URL profonde /dashboard/benevole : ne remplace pas par /dashboard', async () => {
    sessionStorage.setItem('peintre-nano.recyclique.access_token', 'stored-token');
    window.history.pushState({}, '', '/dashboard/benevole');

    render(
      <MantineProvider>
        <LiveAuthShell>
          <span data-testid="post-login-child">in</span>
        </LiveAuthShell>
      </MantineProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('post-login-child')).toBeTruthy();
    });
    expect(window.location.pathname).toBe('/dashboard/benevole');
    expect(fetchRecycliqueContextEnvelope).toHaveBeenCalledWith('stored-token');
  });

  it('restauration : erreur serveur 500 sur le contexte conserve le jeton pour retry manuel', async () => {
    sessionStorage.setItem('peintre-nano.recyclique.access_token', 'bad-restored-token');
    fetchRecycliqueContextEnvelope.mockResolvedValue({
      ok: false,
      status: 500,
      message: 'GET /v1/users/me/context a échoué (500) : Internal Server Error',
    });

    render(
      <MantineProvider>
        <LiveAuthShell>
          <span data-testid="post-login-child">in</span>
        </LiveAuthShell>
      </MantineProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('live-auth-public-shell')).toBeTruthy();
    });
    expect(sessionStorage.getItem('peintre-nano.recyclique.access_token')).toBe('bad-restored-token');
    expect(screen.queryByTestId('post-login-child')).toBeNull();
    expect(screen.getByRole('button', { name: 'Réessayer la connexion' })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Oublier la session sur cet appareil' })).toBeTruthy();
  });

  it('route /shared-workstation/enroll sans session : enfant rendu, pas de shell login (Story 27.4)', async () => {
    window.history.pushState({}, '', '/shared-workstation/enroll');

    render(
      <MantineProvider>
        <LiveAuthShell>
          <span data-testid="enroll-child">enroll</span>
        </LiveAuthShell>
      </MantineProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('enroll-child')).toBeTruthy();
    });
    expect(screen.queryByTestId('live-auth-public-shell')).toBeNull();
    expect(screen.queryByRole('textbox', { name: /Nom d'utilisateur/ })).toBeNull();
    expect(window.location.pathname).toBe('/shared-workstation/enroll');
  });

  it('Story 27.6 CR-1 : poste enrôlé — enfant masqué pendant loading puis visible si session active', async () => {
    hasDeviceIdentity.mockResolvedValue(true);
    let resolveStatus!: (value: Awaited<ReturnType<typeof fetchOperatorSessionStatus>>) => void;
    fetchOperatorSessionStatus.mockReturnValue(
      new Promise((resolve) => {
        resolveStatus = resolve;
      }),
    );

    render(
      <MantineProvider>
        <LiveAuthShell>
          <span data-testid="post-login-child">in</span>
        </LiveAuthShell>
      </MantineProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('live-auth-public-shell')).toBeTruthy();
    });

    fireEvent.change(screen.getByRole('textbox', { name: /Nom d'utilisateur/ }), {
      target: { value: 'admin' },
    });
    fireEvent.change(screen.getByLabelText(/Mot de passe/), {
      target: { value: 'secret' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Se connecter' }));

    await waitFor(() => {
      expect(screen.queryByTestId('live-auth-public-shell')).toBeNull();
    });
    expect(screen.queryByTestId('post-login-child')).toBeNull();

    resolveStatus({
      ok: true,
      active: true,
      operator_user_id: 'u-op',
      session_id: 'sess-1',
      last_activity_at: null,
      inactivity_timeout_seconds: null,
      seconds_until_lock: null,
    });

    await waitFor(() => {
      expect(screen.getByTestId('post-login-child')).toBeTruthy();
    });
    expect(screen.queryByTestId('shared-workstation-lock-screen')).toBeNull();
  });

  it('Story 27.6 : admin sans identité poste — pas de lock screen après login', async () => {
    render(
      <MantineProvider>
        <LiveAuthShell>
          <span data-testid="post-login-child">in</span>
        </LiveAuthShell>
      </MantineProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('live-auth-public-shell')).toBeTruthy();
    });

    fireEvent.change(screen.getByRole('textbox', { name: /Nom d'utilisateur/ }), {
      target: { value: 'admin' },
    });
    fireEvent.change(screen.getByLabelText(/Mot de passe/), {
      target: { value: 'secret' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Se connecter' }));

    await waitFor(() => {
      expect(screen.getByTestId('post-login-child')).toBeTruthy();
    });
    expect(screen.queryByTestId('shared-workstation-lock-screen')).toBeNull();
  });

  it('route enroll avec jeton invalide (500 contexte) : shell login retry, pas enfant seul (11.2 + 27.4)', async () => {
    sessionStorage.setItem('peintre-nano.recyclique.access_token', 'bad-restored-token');
    window.history.pushState({}, '', '/shared-workstation/enroll');
    fetchRecycliqueContextEnvelope.mockResolvedValue({
      ok: false,
      status: 500,
      message: 'GET /v1/users/me/context a échoué (500) : Internal Server Error',
    });

    render(
      <MantineProvider>
        <LiveAuthShell>
          <span data-testid="enroll-child">enroll</span>
        </LiveAuthShell>
      </MantineProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('live-auth-public-shell')).toBeTruthy();
    });
    expect(screen.queryByTestId('enroll-child')).toBeNull();
    expect(screen.getByRole('button', { name: 'Réessayer la connexion' })).toBeTruthy();
  });
});
