/**
 * Tests ProfilPage — Story 11.1. Smoke : non connecté redirige vers /login.
 */
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { AuthProvider } from './AuthContext';
import { ProfilPage } from './ProfilPage';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importOriginal) => {
  const orig = await importOriginal<typeof import('react-router-dom')>();
  return {
    ...orig,
    useNavigate: () => mockNavigate,
  };
});

function renderProfilPage() {
  return render(
    <MantineProvider>
      <AuthProvider>
        <MemoryRouter>
          <ProfilPage />
        </MemoryRouter>
      </AuthProvider>
    </MantineProvider>
  );
}

describe('ProfilPage', () => {
  it('sans utilisateur connecté redirige vers /login', () => {
    renderProfilPage();
    expect(mockNavigate).toHaveBeenCalledWith('/login', { replace: true });
  });
});
