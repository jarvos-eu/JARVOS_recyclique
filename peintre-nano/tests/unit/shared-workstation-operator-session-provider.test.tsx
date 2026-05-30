// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  SharedWorkstationOperatorSessionProvider,
  useSharedWorkstationLockRequired,
} from '../../src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider';

const { hasDeviceIdentity } = vi.hoisted(() => ({
  hasDeviceIdentity: vi.fn(async () => true),
}));

const { fetchOperatorSessionStatus } = vi.hoisted(() => ({
  fetchOperatorSessionStatus: vi.fn(),
}));

vi.mock('../../src/domains/shared-workstation/device-identity-store', () => ({
  hasDeviceIdentity,
  loadDeviceIdentity: vi.fn(async () => null),
  sharedWorkstationAuthHeaders: vi.fn(async () => ({})),
}));

vi.mock('../../src/api/shared-workstation-operator-pin-client', () => ({
  fetchOperatorSessionStatus,
  verifySharedWorkstationOperatorPin: vi.fn(),
}));

function LockRequiredProbe() {
  const lockRequired = useSharedWorkstationLockRequired();
  return (
    <span data-testid="lock-required">{lockRequired ? 'yes' : 'no'}</span>
  );
}

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe('useSharedWorkstationLockRequired (Story 27.6 CR-1)', () => {
  it('retourne false hors provider (harness réception 7.x sans crash)', () => {
    render(<LockRequiredProbe />);
    expect(screen.getByTestId('lock-required').textContent).toBe('no');
  });

  it('retourne true pendant loading avec poste enrôlé', async () => {
    let resolveStatus!: (value: Awaited<ReturnType<typeof fetchOperatorSessionStatus>>) => void;
    const pending = new Promise<Awaited<ReturnType<typeof fetchOperatorSessionStatus>>>(
      (resolve) => {
        resolveStatus = resolve;
      },
    );
    fetchOperatorSessionStatus.mockReturnValue(pending);
    hasDeviceIdentity.mockResolvedValue(true);

    render(
      <SharedWorkstationOperatorSessionProvider enabled>
        <LockRequiredProbe />
      </SharedWorkstationOperatorSessionProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('lock-required').textContent).toBe('yes');
    });

    resolveStatus({
      ok: true,
      active: true,
      operator_user_id: 'u1',
      session_id: 'sess-1',
    });

    await waitFor(() => {
      expect(screen.getByTestId('lock-required').textContent).toBe('no');
    });
  });

  it('retourne false sans identité poste', async () => {
    hasDeviceIdentity.mockResolvedValue(false);
    fetchOperatorSessionStatus.mockResolvedValue({
      ok: true,
      active: false,
      operator_user_id: null,
      session_id: null,
    });

    render(
      <SharedWorkstationOperatorSessionProvider enabled>
        <LockRequiredProbe />
      </SharedWorkstationOperatorSessionProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('lock-required').textContent).toBe('no');
    });
  });
});
