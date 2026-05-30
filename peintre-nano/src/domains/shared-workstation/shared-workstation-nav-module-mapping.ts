/**
 * Mapping CREOS navigation → module_key registre (Story 27.7).
 * Projection UI uniquement — l'autorité reste côté serveur.
 */
import type { NavigationEntry } from '../../types/navigation-manifest';

const NAV_ENTRY_MODULE_KEY: Readonly<Record<string, string>> = {
  'bandeau-live-sandbox': 'kpi-live-banner',
  'reception-nominal': 'reception',
};

export function resolveNavEntryModuleKey(entry: NavigationEntry): string | null {
  if (entry.pageKey && NAV_ENTRY_MODULE_KEY[entry.pageKey]) {
    return NAV_ENTRY_MODULE_KEY[entry.pageKey];
  }
  if (NAV_ENTRY_MODULE_KEY[entry.routeKey]) {
    return NAV_ENTRY_MODULE_KEY[entry.routeKey];
  }
  return null;
}

export function isNavEntryModuleEffective(
  entry: NavigationEntry,
  effectiveModuleKeys: readonly string[],
): boolean {
  const moduleKey = resolveNavEntryModuleKey(entry);
  if (!moduleKey) return true;
  return effectiveModuleKeys.includes(moduleKey);
}
