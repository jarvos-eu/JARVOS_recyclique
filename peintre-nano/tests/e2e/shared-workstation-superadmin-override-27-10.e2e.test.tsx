// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { MantineProvider } from '@mantine/core';
import { SharedWorkstationOverrideShell } from '../../src/domains/shared-workstation/SharedWorkstationOverrideShell';

const sessionState = {
  loading: false,
  hasDevice: true,
  operatorSessionActive: true,
  overrideActive: false,
  canActivateSuperAdminOverride: true,
  overrideSecondsRemaining: null as number | null,
  refreshSessionStatus: vi.fn(async () => true),
};

const activateOverrideMock = vi.fn(async () => ({
  ok: true as const,
  override_active: true,
  override_started_at: '2026-05-30T12:00:00Z',
  override_expires_at: '2026-05-30T12:30:00Z',
}));
const deactivateOverrideMock = vi.fn(async () => ({ ok: true as const, override_active: false }));

vi.mock('../../src/api/shared-workstation-override-client', () => ({
  activateOverride: (...args: unknown[]) => activateOverrideMock(...args),
  deactivateOverride: (...args: unknown[]) => deactivateOverrideMock(...args),
}));

vi.mock('../../src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider', () => ({
  useSharedWorkstationOperatorSession: () => sessionState,
}));

vi.mock('../../src/domains/shared-workstation/SharedWorkstationEffectiveModulesProvider', () => ({
  useSharedWorkstationEffectiveModules: () => ({
    loading: false,
    effectiveModuleKeys: [],
    refreshEffectiveModules: vi.fn(async () => []),
  }),
}));

describe('shared-workstation-superadmin-override-27-10 e2e', () => {
  beforeAll(() => {
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  afterEach(() => {
    cleanup();
    sessionState.overrideActive = false;
    sessionState.canActivateSuperAdminOverride = true;
    sessionState.overrideSecondsRemaining = null;
    vi.clearAllMocks();
  });

  it('flux activate → bandeau → deactivate', async () => {
    render(
      <MantineProvider>
        <SharedWorkstationOverrideShell />
      </MantineProvider>,
    );

    fireEvent.click(screen.getByTestId('shared-workstation-override-activate'));
    await waitFor(() =>
      expect(screen.getByTestId('shared-workstation-override-pin')).toBeTruthy(),
    );
    fireEvent.change(screen.getByTestId('shared-workstation-override-pin'), {
      target: { value: '4242' },
    });
    fireEvent.click(screen.getByTestId('shared-workstation-override-confirm'));

    await waitFor(() => expect(activateOverrideMock).toHaveBeenCalledWith('4242'));
    await waitFor(() => expect(sessionState.refreshSessionStatus).toHaveBeenCalled());

    sessionState.overrideActive = true;
    sessionState.canActivateSuperAdminOverride = false;
    sessionState.overrideSecondsRemaining = 1800;

    cleanup();
    render(
      <MantineProvider>
        <SharedWorkstationOverrideShell />
      </MantineProvider>,
    );

    expect(screen.getByTestId('shared-workstation-override-banner')).toBeTruthy();
    fireEvent.click(screen.getByTestId('shared-workstation-override-exit'));
    await waitFor(() => expect(deactivateOverrideMock).toHaveBeenCalledWith('user_exit'));
  });
});
