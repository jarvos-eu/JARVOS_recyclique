/**
 * Tests SignupPage — Story 11.1. Smoke : rendu formulaire inscription.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { SignupPage } from './SignupPage';

function renderSignupPage() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <SignupPage />
      </MemoryRouter>
    </MantineProvider>
  );
}

describe('SignupPage', () => {
  it('affiche le titre Inscription et le formulaire', () => {
    renderSignupPage();
    expect(screen.getByRole('heading', { name: /inscription/i })).toBeInTheDocument();
    expect(screen.getByTestId('signup-form')).toBeInTheDocument();
  });
});
