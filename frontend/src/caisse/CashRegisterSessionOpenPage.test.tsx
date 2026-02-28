/**
 * Tests CashRegisterSessionOpenPage — Story 5.1, 11.2 (Vitest + RTL + MantineProvider).
 */
import { useEffect } from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AuthProvider, useAuth } from '../auth/AuthContext';
import { CashRegisterSessionOpenPage } from './CashRegisterSessionOpenPage';

vi.mock('../api/caisse', () => ({
  getCashRegisters: vi.fn().mockResolvedValue([{ id: 'r1', name: 'Caisse 1', site_id: 's1', location: null, is_active: true, enable_virtual: false, enable_deferred: false, started_at: null, started_by_user_id: null, created_at: '', updated_at: '' }]),
  getCashSessionDeferredCheck: vi.fn().mockResolvedValue({ date: '2026-02-27', has_session: false, session_id: null }),
  openCashSession: vi.fn().mockResolvedValue({}),
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
        <BrowserRouter>
          <CashRegisterSessionOpenPage />
        </BrowserRouter>
      </AuthProvider>
    </MantineProvider>
  );
}

describe('CashRegisterSessionOpenPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders ouverture session title', async () => {
    renderWithRouter();
    expect(await screen.findByRole('heading', { name: /ouverture de session/i })).toBeInTheDocument();
  });

  it('has page test id', async () => {
    renderWithRouter();
    expect(screen.getByTestId('page-session-open')).toBeInTheDocument();
  });

  it('has session type select and submit button', async () => {
    renderWithRouter();
    expect(await screen.findByTestId('session-open-type')).toBeInTheDocument();
    expect(await screen.findByTestId('session-open-submit')).toBeInTheDocument();
  });
});
