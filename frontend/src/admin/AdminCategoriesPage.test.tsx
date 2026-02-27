/**
 * Tests AdminCategoriesPage — Story 8.3.
 * Vitest + RTL + MantineProvider.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminCategoriesPage } from './AdminCategoriesPage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

const mockGetCategoriesHierarchy = vi.fn();
const mockGetExportCsv = vi.fn();
const mockGetImportTemplate = vi.fn();
const mockPostImportAnalyze = vi.fn();
const mockPostImportExecute = vi.fn();
const mockDeleteCategory = vi.fn();
const mockRestoreCategory = vi.fn();
const mockHardDeleteCategory = vi.fn();
const mockGetCategoryHasUsage = vi.fn();
vi.mock('../api/categories', () => ({
  getCategoriesHierarchy: (...args: unknown[]) => mockGetCategoriesHierarchy(...args),
  getExportCsv: (...args: unknown[]) => mockGetExportCsv(...args),
  getImportTemplate: (...args: unknown[]) => mockGetImportTemplate(...args),
  postImportAnalyze: (...args: unknown[]) => mockPostImportAnalyze(...args),
  postImportExecute: (...args: unknown[]) => mockPostImportExecute(...args),
  deleteCategory: (...args: unknown[]) => mockDeleteCategory(...args),
  restoreCategory: (...args: unknown[]) => mockRestoreCategory(...args),
  hardDeleteCategory: (...args: unknown[]) => mockHardDeleteCategory(...args),
  getCategoryHasUsage: (...args: unknown[]) => mockGetCategoryHasUsage(...args),
}));

function renderWithProviders() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <AdminCategoriesPage />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminCategoriesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      accessToken: 'token',
      permissions: ['admin'],
    });
    mockGetCategoriesHierarchy.mockResolvedValue([]);
  });

  it('renders page with breadcrumb and title', async () => {
    renderWithProviders();
    await screen.findByTestId('admin-categories-loading');
    expect(screen.getByTestId('admin-categories-page')).toBeInTheDocument();
    expect(screen.getByTestId('admin-categories-breadcrumb')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Catégories/ })).toBeInTheDocument();
  });

  it('shows Import, Export and Download template buttons', async () => {
    renderWithProviders();
    await screen.findByTestId('admin-categories-table');
    expect(screen.getByTestId('admin-categories-import')).toBeInTheDocument();
    expect(screen.getByTestId('admin-categories-export')).toBeInTheDocument();
    expect(screen.getByTestId('admin-categories-download-template')).toBeInTheDocument();
  });

  it('shows forbidden when user lacks admin permission', () => {
    mockUseAuth.mockReturnValue({ accessToken: null, permissions: ['operator'] });
    renderWithProviders();
    expect(screen.getByTestId('admin-categories-forbidden')).toBeInTheDocument();
  });

  it('shows empty state when no categories', async () => {
    renderWithProviders();
    await screen.findByTestId('admin-categories-empty');
    expect(screen.getByTestId('admin-categories-table')).toBeInTheDocument();
  });

  it('shows categories table with hierarchy when data loaded', async () => {
    mockGetCategoriesHierarchy.mockResolvedValue([
      {
        id: 'c1',
        name: 'Cat A',
        parent_id: null,
        official_name: 'Official A',
        is_visible_sale: true,
        is_visible_reception: true,
        display_order: 0,
        display_order_entry: 0,
        deleted_at: null,
        created_at: '',
        updated_at: '',
        children: [],
      },
    ]);
    renderWithProviders();
    await screen.findByTestId('category-row-c1');
    expect(screen.getByText('Cat A')).toBeInTheDocument();
    expect(screen.getByText('Official A')).toBeInTheDocument();
    expect(screen.getByTestId('soft-delete-c1')).toBeInTheDocument();
    expect(screen.getByTestId('hard-delete-c1')).toBeInTheDocument();
  });

  it('shows Restaurer for deleted category', async () => {
    mockGetCategoriesHierarchy.mockResolvedValue([
      {
        id: 'c2',
        name: 'Cat supprimée',
        parent_id: null,
        official_name: null,
        is_visible_sale: false,
        is_visible_reception: false,
        display_order: 0,
        display_order_entry: 0,
        deleted_at: '2026-01-01T00:00:00Z',
        created_at: '',
        updated_at: '',
        children: [],
      },
    ]);
    renderWithProviders();
    await screen.findByTestId('category-row-c2');
    expect(screen.getByTestId('restore-c2')).toBeInTheDocument();
  });
});
