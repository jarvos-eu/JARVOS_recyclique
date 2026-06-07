// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { CaisseSessionCloseSurface } from '../../src/domains/cashflow/CaisseSessionCloseSurface';
import { resetCoalescedGetCurrentOpenCashSessionForTests } from '../../src/domains/cashflow/caisse-current-session-coalesce';
import * as cashflowDraftStore from '../../src/domains/cashflow/cashflow-draft-store';
import '../../src/registry';

const SESSION_ID = '00000000-0000-4000-8000-000000000099';

beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    configurable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }),
  });
});

describe('Story 28.1 — CaisseSessionCloseSurface reset draft (REV-02)', () => {
  let resetDraftSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    vi.stubGlobal(
      'ResizeObserver',
      class {
        observe(): void {}
        unobserve(): void {}
        disconnect(): void {}
      },
    );
    cashflowDraftStore.resetCashflowDraft();
    cashflowDraftStore.setCashSessionIdInput(SESSION_ID);
    resetDraftSpy = vi.spyOn(cashflowDraftStore, 'resetCashflowDraft');
  });

  afterEach(() => {
    cleanup();
    cashflowDraftStore.resetCashflowDraft();
    resetCoalescedGetCurrentOpenCashSessionForTests();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('postClose succès → resetCashflowDraft appelé', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/cash-sessions/current')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({
              id: SESSION_ID,
              initial_amount: 50,
              current_amount: 50,
              status: 'open',
              total_sales: 0,
              total_items: 0,
              total_donations: 0,
            }),
        });
      }
      if (url.includes('/close') && method === 'POST') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({
              id: SESSION_ID,
              status: 'closed',
            }),
        });
      }
      return Promise.resolve({ ok: true, status: 200, text: async () => '{}' });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <RootProviders disableUserPrefsPersistence>
        <CaisseSessionCloseSurface salePath="/cash-register/sale" />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('cashflow-session-close-pin-empty')).toBeTruthy();
    });

    fireEvent.change(screen.getByTestId('cashflow-session-close-pin-empty'), {
      target: { value: '1234' },
    });
    fireEvent.click(screen.getByTestId('cashflow-session-close-empty-continue'));

    await waitFor(() => {
      expect(resetDraftSpy).toHaveBeenCalled();
    });

    const closePosts = fetchMock.mock.calls.filter(
      (c) =>
        (typeof c[0] === 'string' ? c[0] : c[0] instanceof URL ? c[0].href : c[0].url).includes(
          '/close',
        ) && (c[1]?.method ?? 'GET').toUpperCase() === 'POST',
    );
    expect(closePosts.length).toBe(1);
  });
});
