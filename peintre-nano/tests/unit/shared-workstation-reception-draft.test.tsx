// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { MantineProvider } from '@mantine/core';
import { SharedWorkstationReceptionDraftResumePanel } from '../../src/domains/shared-workstation/SharedWorkstationReceptionDraftResumePanel';

vi.mock('../../src/api/shared-workstation-reception-draft-client', () => ({
  resumeSharedWorkstationReceptionDraft: vi.fn(async () => ({
    ok: true,
    poste_id: 'poste-1',
    ticket_id: 'ticket-1',
  })),
  abandonSharedWorkstationReceptionDraft: vi.fn(async () => ({ ok: true })),
}));

function renderPanel() {
  const onResumed = vi.fn();
  const onAbandoned = vi.fn();
  render(
    <MantineProvider>
      <SharedWorkstationReceptionDraftResumePanel
        accessToken="token-test"
        summary={{
          poste_id: 'poste-1',
          ticket_id: 'ticket-1',
          started_by_display: 'Alice',
          started_at: '2026-05-30T10:00:00.000Z',
          line_count: 0,
        }}
        onResumed={onResumed}
        onAbandoned={onAbandoned}
      />
    </MantineProvider>,
  );
  return { onResumed, onAbandoned };
}

describe('SharedWorkstationReceptionDraftResumePanel', () => {
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

  it('affiche le résumé autorisé sans lignes', () => {
    renderPanel();
    expect(screen.getByTestId('shared-workstation-reception-draft-panel')).toBeTruthy();
    expect(screen.getByText(/Alice/)).toBeTruthy();
    expect(screen.queryByTestId('reception-ticket-detail')).toBeNull();
  });

  it('reprend le brouillon après confirmation', async () => {
    const { onResumed } = renderPanel();
    fireEvent.click(screen.getByTestId('reception-draft-resume'));
    await waitFor(() => {
      expect(onResumed).toHaveBeenCalledWith('poste-1', 'ticket-1');
    });
  });

  it('abandonne le brouillon après double confirmation UI', async () => {
    const { onAbandoned } = renderPanel();
    fireEvent.click(screen.getByTestId('reception-draft-abandon'));
    expect(screen.getByText('Confirmer abandon')).toBeTruthy();
    fireEvent.click(screen.getByTestId('reception-draft-abandon'));
    await waitFor(() => {
      expect(onAbandoned).toHaveBeenCalled();
    });
  });
});
