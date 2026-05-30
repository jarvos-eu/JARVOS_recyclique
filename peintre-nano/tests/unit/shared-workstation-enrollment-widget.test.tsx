// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import type { ReactElement } from 'react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { SharedWorkstationEnrollmentWidget } from '../../src/domains/shared-workstation/SharedWorkstationEnrollmentWidget';
import '../../src/styles/tokens.css';

vi.mock('../../src/domains/shared-workstation/device-identity-store', () => ({
  hasDeviceIdentity: vi.fn(async () => false),
  hadPriorDeviceEnrollment: vi.fn(async () => false),
  saveDeviceIdentity: vi.fn(async () => undefined),
  loadDeviceIdentity: vi.fn(async () => null),
  clearDeviceIdentity: vi.fn(async () => undefined),
}));

vi.mock('../../src/api/shared-workstation-enrollment-client', () => ({
  completeSharedWorkstationEnrollment: vi.fn(async () => ({
    ok: true,
    device_id: '660e8400-e29b-41d4-a716-446655440001',
    device_secret: 'sec-test',
    device_name: 'Poste Hall',
    site_id: '550e8400-e29b-41d4-a716-446655440000',
  })),
}));

import { completeSharedWorkstationEnrollment } from '../../src/api/shared-workstation-enrollment-client';
import {
  hadPriorDeviceEnrollment,
  hasDeviceIdentity,
  saveDeviceIdentity,
} from '../../src/domains/shared-workstation/device-identity-store';

function wrap(ui: ReactElement) {
  return <RootProviders>{ui}</RootProviders>;
}

describe('SharedWorkstationEnrollmentWidget', () => {
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
    globalThis.ResizeObserver = class {
      observe(): void {}
      unobserve(): void {}
      disconnect(): void {}
    } as typeof ResizeObserver;
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it('saisie code → complete API → save identity IndexedDB', async () => {
    render(wrap(<SharedWorkstationEnrollmentWidget widgetType="shared-workstation.enrollment" />));
    fireEvent.change(screen.getByTestId('shared-workstation-enrollment-code'), {
      target: { value: 'ABCD2345' },
    });
    fireEvent.click(screen.getByTestId('shared-workstation-enrollment-submit'));
    await waitFor(() => {
      expect(completeSharedWorkstationEnrollment).toHaveBeenCalledWith({ code: 'ABCD2345' });
      expect(saveDeviceIdentity).toHaveBeenCalledWith({
        device_id: '660e8400-e29b-41d4-a716-446655440001',
        device_secret: 'sec-test',
      });
    });
    expect(screen.getByTestId('shared-workstation-enrollment-success')).toBeTruthy();
  });

  it('code expiré → message erreur ENROLLMENT_CODE_EXPIRED', async () => {
    vi.mocked(completeSharedWorkstationEnrollment).mockResolvedValueOnce({
      ok: false,
      code: 'ENROLLMENT_CODE_EXPIRED',
      message: 'Code expiré',
    });

    render(wrap(<SharedWorkstationEnrollmentWidget widgetType="shared-workstation.enrollment" />));
    fireEvent.change(screen.getByTestId('shared-workstation-enrollment-code'), {
      target: { value: 'EXPIRED1' },
    });
    fireEvent.click(screen.getByTestId('shared-workstation-enrollment-submit'));

    await waitFor(() => {
      expect(screen.getByText(/Code expiré — demandez un nouveau code/)).toBeTruthy();
    });
    expect(saveDeviceIdentity).not.toHaveBeenCalled();
  });

  it('hint IndexedDB : bannière identité perdue sans credential actif', async () => {
    vi.mocked(hasDeviceIdentity).mockResolvedValueOnce(false);
    vi.mocked(hadPriorDeviceEnrollment).mockResolvedValueOnce(true);

    render(wrap(<SharedWorkstationEnrollmentWidget widgetType="shared-workstation.enrollment" />));

    await waitFor(() => {
      expect(screen.getByTestId('shared-workstation-identity-lost-banner')).toBeTruthy();
    });
  });

  it('échec saveDeviceIdentity → message erreur, pas de succès', async () => {
    vi.mocked(saveDeviceIdentity).mockRejectedValueOnce(new Error('IndexedDB put failed'));

    render(wrap(<SharedWorkstationEnrollmentWidget widgetType="shared-workstation.enrollment" />));
    fireEvent.change(screen.getByTestId('shared-workstation-enrollment-code'), {
      target: { value: 'ABCD2345' },
    });
    fireEvent.click(screen.getByTestId('shared-workstation-enrollment-submit'));

    await waitFor(() => {
      expect(
        screen.getByText(/identité locale n'a pas pu être enregistrée/i),
      ).toBeTruthy();
    });
    expect(screen.queryByTestId('shared-workstation-enrollment-success')).toBeNull();
  });
});
