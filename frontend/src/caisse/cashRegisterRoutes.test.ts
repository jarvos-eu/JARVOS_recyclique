/**
 * Tests routes caisse (Story 3.5).
 */
import { describe, it, expect } from 'vitest';
import {
  isCaisseAllowedPath,
  CAISSE_DEFAULT_REDIRECT,
  CAISSE_PIN_PATH,
} from './cashRegisterRoutes';

describe('cashRegisterRoutes', () => {
  describe('isCaisseAllowedPath', () => {
    it('autorise /caisse et /cash-register/pin', () => {
      expect(isCaisseAllowedPath('/caisse')).toBe(true);
      expect(isCaisseAllowedPath('/cash-register/pin')).toBe(true);
    });

    it('autorise les sous-routes caisse (artefact 10 §5.1-5.4)', () => {
      expect(isCaisseAllowedPath('/cash-register/virtual')).toBe(true);
      expect(isCaisseAllowedPath('/cash-register/deferred')).toBe(true);
      expect(isCaisseAllowedPath('/cash-register/session/open')).toBe(true);
      expect(isCaisseAllowedPath('/cash-register/sale')).toBe(true);
      expect(isCaisseAllowedPath('/cash-register/session/open/123')).toBe(true);
    });

    it('refuse /admin, /reception, /profil, /admin/categories', () => {
      expect(isCaisseAllowedPath('/admin')).toBe(false);
      expect(isCaisseAllowedPath('/admin/users')).toBe(false);
      expect(isCaisseAllowedPath('/reception')).toBe(false);
      expect(isCaisseAllowedPath('/profil')).toBe(false);
      expect(isCaisseAllowedPath('/admin/categories')).toBe(false);
    });

    it('refuse /admin/cash-sessions/:id (artefact 10 §5.5 — détail session admin, pas menu caisse)', () => {
      expect(isCaisseAllowedPath('/admin/cash-sessions/123')).toBe(false);
      expect(isCaisseAllowedPath('/admin/cash-sessions/abc')).toBe(false);
    });

    it('refuse /login et /signup (hors caisse)', () => {
      expect(isCaisseAllowedPath('/login')).toBe(false);
      expect(isCaisseAllowedPath('/signup')).toBe(false);
    });

    it('normalise le slash final', () => {
      expect(isCaisseAllowedPath('/caisse/')).toBe(true);
    });
  });

  it('CAISSE_DEFAULT_REDIRECT et CAISSE_PIN_PATH sont définis', () => {
    expect(CAISSE_DEFAULT_REDIRECT).toBe('/caisse');
    expect(CAISSE_PIN_PATH).toBe('/cash-register/pin');
  });
});
