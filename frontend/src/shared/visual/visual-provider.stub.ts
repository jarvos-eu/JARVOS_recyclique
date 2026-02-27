/**
 * Stub VisualProvider — v1 : image/URL placeholder, pas d'appel à Peintre.
 * v2+ : remplacer par le client Peintre (JARVOS Mini).
 */
import type { VisualContext, VisualProvider, VisualResult } from './types';

/** URL placeholder (1x1 transparent ou image générique). */
const PLACEHOLDER_URL = 'data:image/svg+xml,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"><rect width="1" height="1" fill="transparent"/></svg>'
);

export const visualProviderStub: VisualProvider = {
  async getVisual(context: VisualContext): Promise<VisualResult> {
    return Promise.resolve({
      url: PLACEHOLDER_URL,
      alt: `Placeholder: ${context.slotId}`,
    });
  },
};
