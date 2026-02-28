/**
 * Tests AdminReportsPage — Story 8.2, 11.4.
 * Vitest + RTL + MantineProvider. Smoke : rendu, liste, export bulk.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminReportsPage } from './AdminReportsPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockGetSites = vi.fn();
const mockGetCashSessionReportsList = vi.fn();
const mockGetReportBySession = vi.fn();
const mockPostExportBulk = vi.fn();
vi.mock('../api/admin', () => ({ getSites: (...args: unknown[]) => mockGetSites(...args) }));
vi.mock('../api/adminReports', () => ({
  getCashSessionReportsList: (...args: unknown[]) => mockGetCashSessionReportsList(...args),
  getReportBySession: (...args: unknown[]) => mockGetReportBySession(...args),
  postExportBulk: (...args: unknown[]) => mockPostExportBulk(...args),
}));

function renderWithProviders() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <AdminReportsPage />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminReportsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({ accessToken: 'token', permissions: ['admin'] });
    mockGetSites.mockResolvedValue([]);
    mockGetCashSessionReportsList.mockResolvedValue([]);
  });

  it('renders page with title and Export bulk button', async () => {
    renderWithProviders();
    await screen.findByTestId('admin-reports-loading');
    expect(screen.getByTestId('admin-reports-page')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Rapports caisse/ })).toBeInTheDocument();
    expect(screen.getByTestId('admin-reports-bulk')).toBeInTheDocument();
  });

  it('shows forbidden when user lacks admin permission', () => {
    mockUseAuth.mockReturnValue({ accessToken: null, permissions: ['operator'] });
    renderWithProviders();
    expect(screen.getByTestId('admin-reports-forbidden')).toBeInTheDocument();
  });

  it('shows empty state when no reports', async () => {
    renderWithProviders();
    await screen.findByTestId('admin-reports-empty');
    expect(screen.getByTestId('admin-reports-table')).toBeInTheDocument();
  });
});
