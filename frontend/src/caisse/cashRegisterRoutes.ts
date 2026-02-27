/**
 * Routes caisse autorisées en mode verrouillé — Story 3.5.
 * Aligné sur artefact 10 §5.1 à §5.4 (pas §5.5 admin).
 * Inclut la route/écran PIN pour déverrouillage.
 */

/** Préfixes et chemins autorisés quand poste caisse actif + verrouillé. */
export const CAISSE_ALLOWED_PATH_PREFIXES = [
  '/caisse',
  '/cash-register/virtual',
  '/cash-register/deferred',
  '/cash-register/session/open',
  '/cash-register/session/close',
  '/cash-register/sale',
  '/cash-register/pin',
] as const;

/** Chemins exacts autorisés (ex. étape exit = même zone ou modal, pas de route dédiée). */
export const CAISSE_ALLOWED_EXACT_PATHS = new Set<string>([
  '/caisse',
  '/cash-register/pin',
  '/cash-register/session/close',
]);

/**
 * Retourne true si le pathname est autorisé en mode caisse verrouillé.
 */
export function isCaisseAllowedPath(pathname: string): boolean {
  const normalized = pathname.replace(/\/$/, '') || '/';
  if (CAISSE_ALLOWED_EXACT_PATHS.has(normalized)) return true;
  return CAISSE_ALLOWED_PATH_PREFIXES.some(
    (prefix) => normalized === prefix || normalized.startsWith(prefix + '/')
  );
}

/**
 * Chemin de redirection par défaut quand accès refusé en mode verrouillé :
 * écran caisse principal (dashboard).
 */
export const CAISSE_DEFAULT_REDIRECT = '/caisse';

/**
 * Chemin vers l'écran PIN (déverrouillage).
 */
export const CAISSE_PIN_PATH = '/cash-register/pin';

/**
 * Chemin vers l'écran Fermeture session (étape exit — artefact 10 §5.4).
 */
export const CAISSE_SESSION_CLOSE_PATH = '/cash-register/session/close';
