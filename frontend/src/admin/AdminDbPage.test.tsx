/**
 * Tests AdminDbPage — Story 8.5.
 * Vitest + RTL + MantineProvider. Mock API et AuthContext.
 */
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminDbPage } from './AdminDbPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockPostAdminDbExport = vi.fn();
const mockPostAdminDbPurgeTransactions = vi.fn();
const mockPostAdminDbImport = vi.fn();
vi.mock('../api/adminDb', () => ({
  postAdminDbExport: (...args: unknown[]) => mockPostAdminDbExport(...args),
  postAdminDbPurgeTransactions: (...args: unknown[]) => mockPostAdminDbPurgeTransactions(...args),
  postAdminDbImport: (...args: unknown[]) => mockPostAdminDbImport(...args),
}));

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <MantineProvider>
      <MemoryRouter>{ui}</MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminDbPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: { id: '1', username: 'admin' },
      permissions: ['admin'],
      accessToken: 'token',
    });
    mockPostAdminDbExport.mockResolvedValue(undefined);
  });

  it('affiche forbidden quand pas admin', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1' },
      permissions: [],
      accessToken: 'token',
    });
    renderWithProviders(<AdminDbPage />);
    expect(screen.getByTestId('admin-db-forbidden')).toBeInTheDocument();
  });

  it('affiche la page BDD avec sections Export, Purge, Import', () => {
    renderWithProviders(<AdminDbPage />);
    expect(screen.getByTestId('admin-db-page')).toBeInTheDocument();
    expect(screen.getByTestId('btn-db-export')).toBeInTheDocument();
    expect(screen.getByTestId('btn-db-purge-open')).toBeInTheDocument();
    expect(screen.getByTestId('btn-db-import')).toBeInTheDocument();
  });

  it('appelle postAdminDbExport au clic sur Export BDD', async () => {
    renderWithProviders(<AdminDbPage />);
    fireEvent.click(screen.getByTestId('btn-db-export'));
    await waitFor(() => {
      expect(mockPostAdminDbExport).toHaveBeenCalledWith('token');
    });
  });
});
