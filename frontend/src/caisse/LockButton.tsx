/**
 * Bouton reverrouiller la caisse — Story 3.3.
 * Remet l'état caisse en verrouillé sans invalider le JWT.
 * Convention projet : Mantine Button.
 */
import React from 'react';
import { Button } from '@mantine/core';
import { useCaisse } from './CaisseContext';

export interface LockButtonProps {
  children?: React.ReactNode;
  className?: string;
  variant?: 'filled' | 'light' | 'outline' | 'default' | 'subtle' | 'gradient';
}

export function LockButton({
  children = 'Reverrouiller',
  className,
  variant = 'light',
}: LockButtonProps) {
  const { lock } = useCaisse();
  return (
    <Button
      type="button"
      variant={variant}
      onClick={lock}
      className={className}
      data-testid="lock-button"
    >
      {children}
    </Button>
  );
}
