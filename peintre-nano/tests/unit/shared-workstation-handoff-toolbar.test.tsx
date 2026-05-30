// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { fireEvent, render, screen } from '@testing-library/react';
import { beforeAll, describe, expect, it, vi } from 'vitest';
import { MantineProvider } from '@mantine/core';
import { SharedWorkstationHandoffToolbar } from '../../src/domains/shared-workstation/SharedWorkstationHandoffToolbar';

describe('SharedWorkstationHandoffToolbar', () => {
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
  it('boutons appellent end avec raison attendue', () => {
    const onEnd = vi.fn();
    render(
      <MantineProvider>
        <SharedWorkstationHandoffToolbar onEndSession={onEnd} />
      </MantineProvider>,
    );

    fireEvent.click(screen.getByTestId('shared-workstation-handoff'));
    expect(onEnd).toHaveBeenCalledWith('handoff');

    fireEvent.click(screen.getByTestId('shared-workstation-lock-now-toolbar'));
    expect(onEnd).toHaveBeenCalledWith('manual_lock');
  });
});
