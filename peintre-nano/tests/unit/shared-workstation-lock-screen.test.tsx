// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { MantineProvider } from '@mantine/core';
import { SharedWorkstationLockScreen } from '../../src/domains/shared-workstation/SharedWorkstationLockScreen';
import { SharedWorkstationOperatorSessionProvider } from '../../src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider';

const { fetchOperatorSessionStatus, verifySharedWorkstationOperatorPin } = vi.hoisted(() => ({
  fetchOperatorSessionStatus: vi.fn(),
  verifySharedWorkstationOperatorPin: vi.fn(),
}));

vi.mock('../../src/domains/shared-workstation/device-identity-store', () => ({
  hasDeviceIdentity: vi.fn(async () => true),
  loadDeviceIdentity: vi.fn(async () => ({
    device_id: '660e8400-e29b-41d4-a716-446655440001',
    device_secret: 'sec',
    enrolled_at: '2026-05-30T00:00:00.000Z',
  })),
  sharedWorkstationAuthHeaders: vi.fn(async () => ({})),
}));

vi.mock('../../src/api/shared-workstation-operator-session-client', () => ({
  fetchOperatorSessionStatus,
}));
vi.mock('../../src/api/shared-workstation-operator-pin-client', () => ({
  verifySharedWorkstationOperatorPin,
}));

describe('SharedWorkstationLockScreen', () => {
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

  it('affiche le lock screen quand session inactive', async () => {
    fetchOperatorSessionStatus.mockResolvedValue({
      ok: true,
      active: false,
      operator_user_id: null,
      session_id: null,
    });

    render(
      <MantineProvider>
        <SharedWorkstationOperatorSessionProvider enabled>
          <SharedWorkstationLockScreen />
        </SharedWorkstationOperatorSessionProvider>
      </MantineProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-lock-screen')).toBeTruthy();
    });
  });

  it('masque après succès PIN mock', async () => {
    fetchOperatorSessionStatus
      .mockResolvedValueOnce({
        ok: true,
        active: false,
        operator_user_id: null,
        session_id: null,
      })
      .mockResolvedValueOnce({
        ok: true,
        active: true,
        operator_user_id: '550e8400-e29b-41d4-a716-446655440000',
        session_id: 'sess',
      });
    verifySharedWorkstationOperatorPin.mockResolvedValue({
      ok: true,
      session_id: 'sess',
      device_id: '660e8400-e29b-41d4-a716-446655440001',
      operator_user_id: '550e8400-e29b-41d4-a716-446655440000',
      site_id: '550e8400-e29b-41d4-a716-446655440001',
      started_at: '2026-05-30T12:00:00Z',
    });

    const onUnlocked = vi.fn();
    render(
      <MantineProvider>
        <SharedWorkstationOperatorSessionProvider enabled>
          <SharedWorkstationLockScreen onUnlocked={onUnlocked} />
        </SharedWorkstationOperatorSessionProvider>
      </MantineProvider>,
    );

    await waitFor(() => screen.getByTestId('shared-workstation-operator-id'));

    fireEvent.change(screen.getByTestId('shared-workstation-operator-id'), {
      target: { value: '550e8400-e29b-41d4-a716-446655440000' },
    });

    const pinRoot = screen.getByTestId('shared-workstation-pin-input');
    const inputs = pinRoot.querySelectorAll('input');
    inputs.forEach((input, i) => {
      fireEvent.change(input, { target: { value: String(i + 1) } });
    });

    fireEvent.click(screen.getByTestId('shared-workstation-pin-submit'));

    await waitFor(() => {
      expect(verifySharedWorkstationOperatorPin).toHaveBeenCalled();
      expect(onUnlocked).toHaveBeenCalled();
    });
  });

  it('PIN non configuré : message neutre identique à PIN invalide (anti-énumération UI)', async () => {
    fetchOperatorSessionStatus.mockResolvedValue({
      ok: true,
      active: false,
      operator_user_id: null,
      session_id: null,
    });
    verifySharedWorkstationOperatorPin.mockResolvedValue({
      ok: false,
      code: 'SHARED_WORKSTATION_PIN_NOT_CONFIGURED',
      status: 403,
    });

    render(
      <MantineProvider>
        <SharedWorkstationOperatorSessionProvider enabled>
          <SharedWorkstationLockScreen />
        </SharedWorkstationOperatorSessionProvider>
      </MantineProvider>,
    );

    await waitFor(() => screen.getByTestId('shared-workstation-operator-id'));

    fireEvent.change(screen.getByTestId('shared-workstation-operator-id'), {
      target: { value: '550e8400-e29b-41d4-a716-446655440000' },
    });

    const pinRoot = screen.getByTestId('shared-workstation-pin-input');
    pinRoot.querySelectorAll('input').forEach((input, i) => {
      fireEvent.change(input, { target: { value: String(i + 1) } });
    });
    fireEvent.click(screen.getByTestId('shared-workstation-pin-submit'));

    await waitFor(() => {
      expect(screen.getByText(/Identifiant ou PIN incorrect/i)).toBeTruthy();
    });
    expect(screen.getByTestId('shared-workstation-lock-screen')).toBeTruthy();
  });
});
