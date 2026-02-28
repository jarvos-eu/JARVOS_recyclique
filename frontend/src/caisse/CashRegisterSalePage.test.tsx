/**
 * Tests Story 5.4, 11.2 — flux hors ligne et synchronisation (Vitest + RTL + MantineProvider).
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { CashRegisterSalePage } from './CashRegisterSalePage';
import * as caisseApi from '../api/caisse';
import * as offlineQueue from './offlineQueue';

// Mock auth
vi.mock('../auth/AuthContext', () => ({
  useAuth: () => ({
    accessToken: 'mock-token',
  }),
}));

// Mock online status (controle pour les tests)
let mockOnline = true;
vi.mock('./useOnlineStatus', () => ({
  useOnlineStatus: () => mockOnline,
}));

// Mock API
const mockGetCurrentCashSession = vi.spyOn(caisseApi, 'getCurrentCashSession');
const mockGetPresetsActive = vi.spyOn(caisseApi, 'getPresetsActive');
const mockGetCategoriesSaleTickets = vi.spyOn(caisseApi, 'getCategoriesSaleTickets');
const mockPostSale = vi.spyOn(caisseApi, 'postSale');
const mockUpdateCashSessionStep = vi.spyOn(caisseApi, 'updateCashSessionStep');

// Mock offline queue
const mockAddTicket = vi.spyOn(offlineQueue, 'addTicket');
const mockGetPendingCount = vi.spyOn(offlineQueue, 'getPendingCount');
const mockSyncOfflineQueue = vi.spyOn(offlineQueue, 'syncOfflineQueue');

const fakeSession = {
  id: 'session-1',
  operator_id: 'op-1',
  register_id: 'reg-1',
  site_id: 'site-1',
  initial_amount: 1000,
  current_amount: 1000,
  status: 'open',
  opened_at: '2026-01-01T10:00:00Z',
  closed_at: null,
  current_step: 'sale',
  closing_amount: null,
  actual_amount: null,
  variance: null,
  variance_comment: null,
  session_type: 'real',
  total_sales: null,
  total_items: null,
  created_at: '2026-01-01T10:00:00Z',
  updated_at: '2026-01-01T10:00:00Z',
};

const fakePresets = [
  {
    id: 'preset-1',
    name: 'Preset 1',
    category_id: null,
    preset_price: 500,
    button_type: 'sale',
    sort_order: 0,
    is_active: true,
    created_at: '',
    updated_at: '',
  },
];

const fakeCategories = [
  {
    id: 'cat-1',
    name: 'Cat 1',
    parent_id: null,
    official_name: null,
    is_visible_sale: true,
    is_visible_reception: false,
    display_order: 0,
    display_order_entry: 0,
    deleted_at: null,
    created_at: '',
    updated_at: '',
  },
];

beforeEach(() => {
  vi.clearAllMocks();
  mockOnline = true;
  mockGetCurrentCashSession.mockResolvedValue(fakeSession as caisseApi.CashSessionItem);
  mockGetPresetsActive.mockResolvedValue(fakePresets as caisseApi.PresetItem[]);
  mockGetCategoriesSaleTickets.mockResolvedValue(fakeCategories as caisseApi.CategoryItem[]);
  mockUpdateCashSessionStep.mockResolvedValue(fakeSession as caisseApi.CashSessionItem);
  mockGetPendingCount.mockResolvedValue(0);
  mockSyncOfflineQueue.mockResolvedValue({ sent: 0, failed: 0, errors: [] });
});

function renderPage() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <CashRegisterSalePage />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('CashRegisterSalePage — Story 5.4 offline & sync', () => {
  it('affiche le bandeau hors ligne quand useOnlineStatus est false', async () => {
    mockOnline = false;
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId('page-sale')).toBeInTheDocument();
    });
    expect(screen.getByTestId('offline-banner')).toBeInTheDocument();
    expect(screen.getByText(/Hors ligne/)).toBeInTheDocument();
  });

  it('en ligne sans tickets en attente : pas de bandeau sync', async () => {
    mockOnline = true;
    mockGetPendingCount.mockResolvedValue(0);
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId('page-sale')).toBeInTheDocument();
    });
    expect(screen.queryByTestId('sync-pending-banner')).not.toBeInTheDocument();
  });

  it('en ligne avec tickets en attente : affiche bandeau synchronisation', async () => {
    mockOnline = true;
    mockGetPendingCount.mockResolvedValue(2);
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId('sync-pending-banner')).toBeInTheDocument();
    });
    expect(screen.getByText(/2 ticket\(s\) à envoyer/)).toBeInTheDocument();
  });

  it('soumission en ligne appelle POST /v1/sales et pas addTicket', async () => {
    mockPostSale.mockResolvedValue({} as caisseApi.SaleResponseItem);
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId('preset-preset-1')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('preset-preset-1'));
    fireEvent.change(screen.getByTestId('payment-amount'), { target: { value: '5' } });
    fireEvent.click(screen.getByTestId('add-payment'));
    fireEvent.click(screen.getByTestId('sale-submit'));

    await waitFor(() => {
      expect(mockPostSale).toHaveBeenCalledWith(
        'mock-token',
        expect.objectContaining({
          cash_session_id: 'session-1',
          items: expect.any(Array),
          payments: expect.any(Array),
        })
      );
    });
    expect(mockAddTicket).not.toHaveBeenCalled();
  });

  it('soumission hors ligne appelle addTicket avec offline_id et pas postSale', async () => {
    mockOnline = false;
    mockAddTicket.mockResolvedValue(undefined);
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId('preset-preset-1')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('preset-preset-1'));
    fireEvent.change(screen.getByTestId('payment-amount'), { target: { value: '5' } });
    fireEvent.click(screen.getByTestId('add-payment'));
    fireEvent.click(screen.getByTestId('sale-submit'));

    await waitFor(() => {
      expect(mockAddTicket).toHaveBeenCalledWith(
        expect.objectContaining({
          cash_session_id: 'session-1',
          items: expect.any(Array),
          payments: expect.any(Array),
          offline_id: expect.any(String),
          created_at: expect.any(String),
        })
      );
    });
    expect(mockPostSale).not.toHaveBeenCalled();
  });
});
