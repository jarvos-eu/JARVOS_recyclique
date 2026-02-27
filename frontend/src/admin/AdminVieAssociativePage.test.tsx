/**
 * Tests AdminVieAssociativePage — Story 8.7.
 * Vitest + RTL + MantineProvider.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';
import { AdminVieAssociativePage } from './AdminVieAssociativePage';

describe('AdminVieAssociativePage', () => {
  it('renders title and placeholder text', () => {
    render(
      <MantineProvider>
        <AdminVieAssociativePage />
      </MantineProvider>
    );
    expect(screen.getByTestId('page-vie-associative')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Vie associative/ })).toBeInTheDocument();
    expect(screen.getByText(/Contenu vie associative à venir/)).toBeInTheDocument();
  });
});
