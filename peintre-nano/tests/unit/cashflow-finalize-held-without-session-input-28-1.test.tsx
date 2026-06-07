// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { KioskFinalizeSaleDock } from '../../src/domains/cashflow/KioskFinalizeSaleDock';
import {
  applyServerHeldSaleToDraft,
  resetCashflowDraft,
} from '../../src/domains/cashflow/cashflow-draft-store';
import '../../src/registry';

describe('Story 28.1 — held sale sans cashSessionIdInput local', () => {
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
    applyServerHeldSaleToDraft({
      id: 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee',
      total_amount: 12.5,
      items: [
        {
          category: 'EEE-1',
          quantity: 1,
          weight: 1,
          unit_price: 12.5,
          total_price: 12.5,
        },
      ],
    });
  });

  it('active le bouton Ouvrir la finalisation sans UUID session saisi (ticket held)', async () => {
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

    render(
      <RootProviders disableUserPrefsPersistence>
        <KioskFinalizeSaleDock />
      </RootProviders>,
    );

    await waitFor(() => {
      const btn = screen.getByTestId('cashflow-submit-sale') as HTMLButtonElement;
      expect(btn.disabled).toBe(false);
    });
    expect(screen.queryByTestId('cashflow-kiosk-finalize-blocked-reason')).toBeNull();
  });
});
