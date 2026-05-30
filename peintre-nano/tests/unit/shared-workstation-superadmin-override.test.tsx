// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { MantineProvider } from '@mantine/core';
import { SharedWorkstationSuperAdminOverrideBanner } from '../../src/domains/shared-workstation/SharedWorkstationSuperAdminOverrideBanner';
import { SharedWorkstationOverrideActivateControl } from '../../src/domains/shared-workstation/SharedWorkstationOverrideActivateControl';
import { SharedWorkstationOverrideActivateModal } from '../../src/domains/shared-workstation/SharedWorkstationOverrideActivateModal';

const activateOverrideMock = vi.fn(async () => ({
  ok: true as const,
  override_active: true,
  override_started_at: '2026-05-30T12:00:00Z',
  override_expires_at: '2026-05-30T12:30:00Z',
}));
const deactivateOverrideMock = vi.fn(async () => ({ ok: true as const, override_active: false }));
const refreshSessionStatusMock = vi.fn(async () => true);
const refreshEffectiveModulesMock = vi.fn(async () => []);

vi.mock('../../src/api/shared-workstation-override-client', () => ({
  activateOverride: (...args: unknown[]) => activateOverrideMock(...args),
  deactivateOverride: (...args: unknown[]) => deactivateOverrideMock(...args),
}));

vi.mock('../../src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider', () => ({
  useSharedWorkstationOperatorSession: () => ({
    loading: false,
    hasDevice: true,
    operatorSessionActive: true,
    overrideActive: false,
    canActivateSuperAdminOverride: true,
    overrideSecondsRemaining: null,
    refreshSessionStatus: refreshSessionStatusMock,
  }),
}));

vi.mock('../../src/domains/shared-workstation/SharedWorkstationEffectiveModulesProvider', () => ({
  useSharedWorkstationEffectiveModules: () => ({
    loading: false,
    effectiveModuleKeys: [],
    refreshEffectiveModules: refreshEffectiveModulesMock,
  }),
}));

describe('shared-workstation-superadmin-override UI', () => {
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
    vi.clearAllMocks();
  });

  it('bandeau visible si override actif avec countdown', () => {
    render(
      <MantineProvider>
        <SharedWorkstationSuperAdminOverrideBanner
          overrideSecondsRemaining={1200}
          onExit={vi.fn()}
        />
      </MantineProvider>,
    );
    expect(screen.getByTestId('shared-workstation-override-banner')).toBeTruthy();
    expect(screen.getByTestId('shared-workstation-override-countdown').textContent).toBe('1200');
  });

  it('contrôle activation visible', () => {
    render(
      <MantineProvider>
        <SharedWorkstationOverrideActivateControl onOpen={vi.fn()} />
      </MantineProvider>,
    );
    expect(screen.getByTestId('shared-workstation-override-activate')).toBeTruthy();
  });

  it('modale activation appelle API activateOverride', async () => {
    const onConfirm = vi.fn(async (pin: string) => {
      await activateOverrideMock(pin);
      return true;
    });
    render(
      <MantineProvider>
        <SharedWorkstationOverrideActivateModal
          opened
          onClose={vi.fn()}
          onConfirm={onConfirm}
        />
      </MantineProvider>,
    );
    fireEvent.change(screen.getByTestId('shared-workstation-override-pin'), {
      target: { value: '4242' },
    });
    fireEvent.click(screen.getByTestId('shared-workstation-override-confirm'));
    await waitFor(() => expect(activateOverrideMock).toHaveBeenCalledWith('4242'));
  });

  it('exit bandeau appelle deactivate', async () => {
    const onExit = vi.fn(async () => {
      await deactivateOverrideMock('user_exit');
    });
    render(
      <MantineProvider>
        <SharedWorkstationSuperAdminOverrideBanner
          overrideSecondsRemaining={600}
          onExit={onExit}
        />
      </MantineProvider>,
    );
    fireEvent.click(screen.getByTestId('shared-workstation-override-exit'));
    await waitFor(() => expect(deactivateOverrideMock).toHaveBeenCalledWith('user_exit'));
  });
});

describe('SharedWorkstationOverrideShell flux', () => {
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
    vi.clearAllMocks();
  });

  it('monte contrôle activation quand can_activate true', async () => {
    const { SharedWorkstationOverrideShell } = await import(
      '../../src/domains/shared-workstation/SharedWorkstationOverrideShell'
    );
    render(
      <MantineProvider>
        <SharedWorkstationOverrideShell />
      </MantineProvider>,
    );
    expect(screen.getByTestId('shared-workstation-override-activate')).toBeTruthy();
  });
});
