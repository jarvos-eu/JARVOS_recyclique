/**
 * Tests CaisseDashboardPage — Story 5.1, 11.2 (Vitest + RTL + MantineProvider).
 */
import { useEffect } from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AuthProvider, useAuth } from '../auth/AuthContext';
import { CaisseProvider } from './CaisseContext';
import { CaisseDashboardPage } from './CaisseDashboardPage';

vi.mock('../api/caisse', () => ({
  getCashRegisters: vi.fn().mockResolvedValue([]),
  getCashRegistersStatus: vi.fn().mockResolvedValue([]),
  getCashSessionStatus: vi.fn().mockResolvedValue({ has_open_session: false, register_id: '', session_id: null, opened_at: null }),
  getCurrentCashSession: vi.fn().mockResolvedValue(null),
}));

function SetToken({ token }: { token: string }) {
  const { setTokens } = useAuth();
  useEffect(() => {
    setTokens(token, null);
  }, [setTokens, token]);
  return null;
}

function renderWithRouter() {
  return render(
    <MantineProvider>
      <AuthProvider>
        <SetToken token="fake-token" />
        <CaisseProvider>
          <BrowserRouter>
            <CaisseDashboardPage />
          </BrowserRouter>
        </CaisseProvider>
      </AuthProvider>
    </MantineProvider>
  );
}

describe('CaisseDashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard title', async () => {
    renderWithRouter();
    expect(screen.getByRole('heading', { name: /dashboard caisses/i })).toBeInTheDocument();
  });

  it('has dashboard page test id', async () => {
    renderWithRouter();
    expect(screen.getByTestId('caisse-dashboard-page')).toBeInTheDocument();
  });
});
