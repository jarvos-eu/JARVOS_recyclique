/**
 * Tests useCashRegisterLock — Story 3.5.
 */
import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AuthProvider } from '../auth/AuthContext';
import { CaisseProvider, useCaisse } from './CaisseContext';
import { useCashRegisterLock } from './useCashRegisterLock';

function ShowLockState() {
  const state = useCashRegisterLock();
  return (
    <div data-testid="lock-state">
      <span data-testid="restricted">{String(state.isRestricted)}</span>
      <span data-testid="active">{String(state.isCashRegisterActive)}</span>
      <span data-testid="locked">{String(state.isLocked)}</span>
      <span data-testid="path-caisse">{String(state.isPathAllowed('/caisse'))}</span>
      <span data-testid="path-admin">{String(state.isPathAllowed('/admin'))}</span>
    </div>
  );
}

function renderWithCaisse(ui: React.ReactElement) {
  return render(
    <AuthProvider>
      <CaisseProvider>
        {ui}
      </CaisseProvider>
    </AuthProvider>
  );
}

describe('useCashRegisterLock', () => {
  it('isRestricted est false quand pas de poste actif', () => {
    renderWithCaisse(<ShowLockState />);
    expect(screen.getByTestId('restricted')).toHaveTextContent('false');
    expect(screen.getByTestId('active')).toHaveTextContent('false');
  });

  it('isRestricted est true quand poste actif + verrouillé', () => {
    function SetRegisterAndShow() {
      const { setCurrentRegister } = useCaisse();
      React.useEffect(() => {
        setCurrentRegister('r1', true);
      }, [setCurrentRegister]);
      return <ShowLockState />;
    }
    renderWithCaisse(<SetRegisterAndShow />);
    expect(screen.getByTestId('active')).toHaveTextContent('true');
    expect(screen.getByTestId('locked')).toHaveTextContent('true');
    expect(screen.getByTestId('restricted')).toHaveTextContent('true');
  });

  it('isPathAllowed retourne true pour /caisse et false pour /admin', () => {
    renderWithCaisse(<ShowLockState />);
    expect(screen.getByTestId('path-caisse')).toHaveTextContent('true');
    expect(screen.getByTestId('path-admin')).toHaveTextContent('false');
  });
});
