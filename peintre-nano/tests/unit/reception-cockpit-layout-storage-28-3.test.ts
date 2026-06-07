// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  DEFAULT_RECEPTION_COCKPIT_LAYOUT,
  RECEPTION_COCKPIT_LAYOUT_STORAGE_KEY,
  buildCockpitGridTemplateColumns,
  clampReceptionCockpitLayout,
  loadReceptionCockpitLayout,
  saveReceptionCockpitLayout,
} from '../../src/domains/reception/reception-cockpit-layout-storage';

describe('Story 28.3 — persistance layout cockpit', () => {
  afterEach(() => {
    window.localStorage.removeItem(RECEPTION_COCKPIT_LAYOUT_STORAGE_KEY);
  });

  it('charge les ratios par défaut si localStorage vide', () => {
    expect(loadReceptionCockpitLayout()).toEqual(DEFAULT_RECEPTION_COCKPIT_LAYOUT);
  });

  it('retourne les ratios par défaut si JSON localStorage corrompu', () => {
    window.localStorage.setItem(RECEPTION_COCKPIT_LAYOUT_STORAGE_KEY, 'not-json{{{');
    expect(loadReceptionCockpitLayout()).toEqual(DEFAULT_RECEPTION_COCKPIT_LAYOUT);
  });

  it('persiste et recharge les ratios colonnes', () => {
    saveReceptionCockpitLayout({ leftPct: 32, centerPct: 44 });
    expect(loadReceptionCockpitLayout()).toEqual({ leftPct: 32, centerPct: 44 });
  });

  it('borne les colonnes pour garder une colonne droite lisible', () => {
    expect(clampReceptionCockpitLayout(70, 70)).toEqual({ leftPct: 64, centerPct: 18 });
  });

  it('produit une grille CSS à trois zones + poignées', () => {
    const grid = buildCockpitGridTemplateColumns({ leftPct: 30, centerPct: 45 });
    expect(grid).toMatch(/minmax\(20rem, 30fr\)/);
    expect(grid).toMatch(/minmax\(24rem, 45fr\)/);
    expect(grid).toMatch(/minmax\(16rem, 25fr\)/);
  });

  it('ne propage pas si localStorage.setItem lève une erreur', () => {
    const setItem = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new DOMException('QuotaExceededError', 'QuotaExceededError');
    });
    expect(() => saveReceptionCockpitLayout({ leftPct: 32, centerPct: 44 })).not.toThrow();
    expect(loadReceptionCockpitLayout()).toEqual(DEFAULT_RECEPTION_COCKPIT_LAYOUT);
    setItem.mockRestore();
  });
});
