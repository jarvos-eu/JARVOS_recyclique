/**
 * Tests AdminUserCreatePage — Story 8.1.
 * Vitest + RTL + MantineProvider.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AdminUserCreatePage } from './AdminUserCreatePage';

const mockUseAuth = vi.fn();
vi.mock('../auth/AuthContext', () => ({ useAuth: () => mockUseAuth() }));

vi.mock('../api/adminUsers', () => ({
  createUser: vi.fn().mockResolvedValue({ id: 'new-1', username: 'newuser' }),
}));

function renderWithProviders() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <AdminUserCreatePage />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('AdminUserCreatePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      accessToken: 'token',
      permissions: ['admin'],
    });
  });

  it('renders create form with heading and inputs', () => {
    renderWithProviders();
    expect(screen.getByTestId('admin-user-create-page')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Nouvel utilisateur/ })).toBeInTheDocument();
    expect(screen.getByTestId('input-username')).toBeInTheDocument();
    expect(screen.getByTestId('input-email')).toBeInTheDocument();
    expect(screen.getByTestId('input-password')).toBeInTheDocument();
    expect(screen.getByTestId('submit-create-user')).toBeInTheDocument();
  });

  it('shows forbidden when user lacks admin permission', () => {
    mockUseAuth.mockReturnValue({ accessToken: null, permissions: ['operator'] });
    renderWithProviders();
    expect(screen.getByTestId('admin-user-create-forbidden')).toBeInTheDocument();
  });
});
