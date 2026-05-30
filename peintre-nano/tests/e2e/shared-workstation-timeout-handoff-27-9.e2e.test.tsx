// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { MantineProvider } from '@mantine/core';
import { SharedWorkstationInactivityWarningModal } from '../../src/domains/shared-workstation/SharedWorkstationInactivityWarningModal';

describe('SharedWorkstationInactivityWarningModal e2e unit', () => {
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
  });

  it('continuer et verrouiller déclenchent callbacks', async () => {
    const onContinue = vi.fn();
    const onLockNow = vi.fn();
    render(
      <MantineProvider>
        <SharedWorkstationInactivityWarningModal
          opened
          secondsUntilLock={45}
          onContinue={onContinue}
          onLockNow={onLockNow}
        />
      </MantineProvider>,
    );

    expect(screen.getByTestId('shared-workstation-inactivity-warning')).toBeTruthy();
    expect(screen.getByTestId('shared-workstation-inactivity-countdown').textContent).toBe('45');

    fireEvent.click(screen.getByTestId('shared-workstation-inactivity-continue'));
    await waitFor(() => expect(onContinue).toHaveBeenCalled());

    fireEvent.click(screen.getByTestId('shared-workstation-lock-now'));
    await waitFor(() => expect(onLockNow).toHaveBeenCalled());
  });
});
