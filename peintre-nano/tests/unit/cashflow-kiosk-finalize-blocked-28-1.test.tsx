// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { KioskFinalizeSaleDock } from '../../src/domains/cashflow/KioskFinalizeSaleDock';
import {
  addTicketLine,
  resetCashflowDraft,
  setCashSessionIdInput,
  setTotalAmount,
} from '../../src/domains/cashflow/cashflow-draft-store';
import '../../src/registry';

describe('Story 28.1 — cashflow-kiosk-finalize-blocked-reason', () => {
  afterEach(() => {
    cleanup();
    resetCashflowDraft();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  beforeEach(() => {
    vi.stubGlobal(
      'matchMedia',
      vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    );
    resetCashflowDraft();
    vi.spyOn(global, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
      if (url.includes('payment-method-options')) {
        return Promise.resolve(
          new Response(JSON.stringify([{ code: 'cash', label: 'Espèces', kind: 'cash' }]), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          }),
        );
      }
      return Promise.resolve(new Response('not found', { status: 404 }));
    });
  });

  it('affiche le motif quand ticket vide (REV-05)', async () => {
    setCashSessionIdInput('00000000-0000-4000-8000-000000000099');

    render(
      <RootProviders disableUserPrefsPersistence>
        <KioskFinalizeSaleDock />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('cashflow-kiosk-finalize-blocked-reason').textContent).toMatch(/articles/i);
    });
    expect((screen.getByTestId('cashflow-submit-sale') as HTMLButtonElement).disabled).toBe(true);
  });

  it('affiche le motif quand session non résolue malgré des lignes (REV-06)', async () => {
    addTicketLine({
      category: 'EEE-1',
      quantity: 1,
      weight: 1,
      unitPrice: 12,
      totalPrice: 12,
    });
    setTotalAmount(12);

    render(
      <RootProviders disableUserPrefsPersistence>
        <KioskFinalizeSaleDock />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('cashflow-kiosk-finalize-blocked-reason').textContent).toMatch(
        /Session caisse non résolue/i,
      );
    });
    expect((screen.getByTestId('cashflow-submit-sale') as HTMLButtonElement).disabled).toBe(true);
  });
});
