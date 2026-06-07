import { describe, expect, it } from 'vitest';
import {
  firstDeferredRegisterId,
  firstVirtualRegisterId,
} from '../../src/domains/cashflow/cashflow-register-variants';

describe('Story 28.1 — résolution poste virtuel / différé (parité legacy)', () => {
  const rows = [
    { id: 'real-1', name: 'Principale', is_open: true, enable_virtual: false, enable_deferred: false },
    { id: 'virt-1', name: 'Formation', is_open: false, enable_virtual: true, enable_deferred: false },
    { id: 'def-1', name: 'Cahier', is_open: false, enable_virtual: false, enable_deferred: true },
  ];

  it('choisit le poste enable_virtual, pas le premier poste réel', () => {
    expect(firstVirtualRegisterId(rows)).toBe('virt-1');
  });

  it('choisit le poste enable_deferred', () => {
    expect(firstDeferredRegisterId(rows)).toBe('def-1');
  });
});
