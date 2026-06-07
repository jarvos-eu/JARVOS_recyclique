/** Badge responsable affiché sur chaque carte recommandation santé (REV-ADMIN-05). */
export type HealthRecommendationResponsibleBadge =
  | 'À faire dans l’application'
  | 'À faire par l’équipe technique / hébergeur'
  | 'Informatif — rien à faire maintenant';

const IN_APP_TYPES = new Set(['cash_control', 'auth_security', 'ops']);
const TECH_TYPES = new Set(['sync_monitoring', 'preventive_sync_optimization', 'preventive_error']);
const INFORMATIVE_LOW_TYPES = new Set(['preventive_database_maintenance', 'preventive_security_review']);

export function healthRecommendationResponsibleBadge(
  type: string,
  priority: string,
): HealthRecommendationResponsibleBadge {
  const t = type.trim().toLowerCase();
  const p = priority.trim().toLowerCase();
  if (INFORMATIVE_LOW_TYPES.has(t) || (t.startsWith('preventive_') && p === 'low')) {
    return 'Informatif — rien à faire maintenant';
  }
  if (IN_APP_TYPES.has(t)) return 'À faire dans l’application';
  if (TECH_TYPES.has(t) || t.startsWith('preventive_')) {
    return 'À faire par l’équipe technique / hébergeur';
  }
  return p === 'low'
    ? 'Informatif — rien à faire maintenant'
    : 'À faire par l’équipe technique / hébergeur';
}

export function healthRecommendationBadgeColor(
  badge: HealthRecommendationResponsibleBadge,
): 'blue' | 'orange' | 'gray' {
  if (badge === 'À faire dans l’application') return 'blue';
  if (badge === 'À faire par l’équipe technique / hébergeur') return 'orange';
  return 'gray';
}
