/**
 * Types et contrat pour la fourniture de visuels (v1 stub, v2+ Peintre / JARVOS Mini).
 * Référence : research technical-affichage-dynamique-peintre-extension-points-research-2026-02-25.
 */

/** Contexte pour demander un visuel (slot, dimensions, options). */
export interface VisualContext {
  /** Identifiant du slot ou de la zone (ex. "header.logo", "caisse.banner"). */
  slotId: string;
  /** Largeur souhaitée en px (optionnel). */
  width?: number;
  /** Hauteur souhaitée en px (optionnel). */
  height?: number;
  /** Options métier (v2+ Peintre). */
  options?: Record<string, unknown>;
}

/** Résultat d'un visuel : URL ou blob. */
export interface VisualResult {
  /** URL d'image (v1 stub : placeholder ; v2+ : Peintre). */
  url?: string;
  /** Données binaires (v2+ si pas d'URL). */
  blob?: Blob;
  /** Texte alternatif. */
  alt?: string;
}

/** Contrat du fournisseur de visuels. Implémenté en stub en v1, client Peintre en v2+. */
export interface VisualProvider {
  /** Retourne un visuel pour le contexte donné. */
  getVisual(context: VisualContext): Promise<VisualResult>;
}
