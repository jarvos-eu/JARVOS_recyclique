/**
 * Types et contrat pour la configuration de layout (v1 stub, v2+ API préférences).
 * Référence : research technical-affichage-dynamique-peintre-extension-points-research-2026-02-25.
 */

/** Contexte optionnel pour demander un layout (v2+ : écran, utilisateur, rôle). */
export interface LayoutContext {
  /** Identifiant d'écran ou de vue (ex. "caisse.dashboard", "reception.accueil"). */
  screenId?: string;
  /** Identifiant utilisateur (v2+ préférences par utilisateur). */
  userId?: string;
}

/** Configuration de layout (structure compatible React-Grid-Layout en v2+). v1 : layout fixe. */
export interface LayoutConfig {
  /** Layout par breakpoint (v2+). v1 : un seul ensemble de positions. */
  layout?: Array<{
    i: string;
    x: number;
    y: number;
    w: number;
    h: number;
    minW?: number;
    minH?: number;
  }>;
  /** Breakpoints (v2+). v1 : non utilisé. */
  breakpoints?: Record<string, number>;
  /** Colonnes par breakpoint (v2+). */
  cols?: Record<string, number>;
}

/** Contrat du service de configuration de layout. Implémenté en stub en v1, API préférences en v2+. */
export interface LayoutConfigService {
  /** Retourne la configuration de layout pour le contexte donné. */
  getLayout(context?: LayoutContext): Promise<LayoutConfig>;
}
