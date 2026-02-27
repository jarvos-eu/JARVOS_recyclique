/**
 * Stub LayoutConfigService — v1 : layout fixe, pas de persistance.
 * v2+ : remplacer par une implémentation qui appelle l'API préférences.
 */
import type { LayoutConfig, LayoutConfigService, LayoutContext } from './types';

const DEFAULT_LAYOUT: LayoutConfig = {
  layout: [],
  breakpoints: { lg: 1200, md: 996, sm: 768 },
  cols: { lg: 12, md: 10, sm: 6 },
};

export const layoutConfigStub: LayoutConfigService = {
  async getLayout(_context?: LayoutContext): Promise<LayoutConfig> {
    return Promise.resolve({ ...DEFAULT_LAYOUT });
  },
};
