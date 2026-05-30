import type { NavigationEntry, NavigationManifest } from '../types/navigation-manifest';
import type { ContextEnvelopeStub } from '../types/context-envelope';
import { isEnvelopeStale } from './context-envelope-freshness';
import { resolveContextMarkersFromEnvelope } from './resolve-context-markers';
import { isNavEntryModuleEffective } from '../domains/shared-workstation/shared-workstation-nav-module-mapping';

/**
 * Options pour `filterNavigation` uniquement (fraîcheur / horloge).
 * Les **UserRuntimePrefs** n’y figurent **pas** : la personnalisation locale ne doit pas influencer le masquage nav.
 */
export type FilterNavigationOptions = {
  readonly nowMs?: number;
  /**
   * Story 27.7 — projection modules effectifs poste partagé (serveur).
   * `null`/`undefined` = pas de filtrage module (utilisateur web classique).
   */
  readonly effectiveModuleKeys?: readonly string[] | null;
};

function entryPermissionKeysSatisfied(entry: NavigationEntry, effective: ReadonlySet<string>): boolean {
  const req = entry.requiredPermissionKeys;
  if (!req?.length) return true;
  return req.every((k) => effective.has(k));
}

/** `permission_any` du manifest : au moins une clé ; cumul avec `required_permission_keys` (AND). */
function entryVisibilityPermissionAnySatisfied(entry: NavigationEntry, effective: ReadonlySet<string>): boolean {
  const anyReq = entry.visibility?.permissionAny;
  if (!anyReq?.length) return true;
  return anyReq.some((k) => effective.has(k));
}

function entryVisibilityContextsSatisfied(entry: NavigationEntry, markers: ReadonlySet<string>): boolean {
  const vis = entry.visibility;
  if (!vis) return true;
  if (vis.contextsAll?.length && !vis.contextsAll.every((m) => markers.has(m))) return false;
  if (vis.contextsAny?.length && !vis.contextsAny.some((m) => markers.has(m))) return false;
  return true;
}

function filterNavEntry(
  entry: NavigationEntry,
  effectivePerms: ReadonlySet<string>,
  contextMarkers: ReadonlySet<string>,
  effectiveModuleKeys: readonly string[] | null | undefined,
): NavigationEntry | null {
  if (!entryVisibilityPermissionAnySatisfied(entry, effectivePerms)) return null;
  if (!entryPermissionKeysSatisfied(entry, effectivePerms)) return null;
  if (!entryVisibilityContextsSatisfied(entry, contextMarkers)) return null;
  if (
    effectiveModuleKeys != null &&
    !isNavEntryModuleEffective(entry, effectiveModuleKeys)
  ) {
    return null;
  }

  if (!entry.children?.length) {
    const { children: _c, ...rest } = entry;
    return rest as NavigationEntry;
  }

  const nextChildren = entry.children
    .map((c) => filterNavEntry(c, effectivePerms, contextMarkers, effectiveModuleKeys))
    .filter((c): c is NavigationEntry => c !== null);

  return {
    ...entry,
    children: nextChildren.length ? nextChildren : undefined,
  };
}

/**
 * Vue filtrée du manifest de navigation : une entrée est exclue si ses `requiredPermissionKeys`
 * ne sont pas couvertes par `envelope.permissions.permissionKeys` (intersection autoritative).
 * Si l'enveloppe est interdite, dégradée ou périmée, aucune entrée n'est exposée (pas de navigation
 * « métier » supposée valide).
 */
export function filterNavigation(
  manifest: NavigationManifest,
  envelope: ContextEnvelopeStub,
  options?: FilterNavigationOptions,
): NavigationManifest {
  const nowMs = options?.nowMs ?? Date.now();
  if (envelope.runtimeStatus === 'forbidden' || envelope.runtimeStatus === 'degraded' || isEnvelopeStale(envelope, nowMs)) {
    return { version: manifest.version, entries: [] };
  }

  const effective = new Set(envelope.permissions.permissionKeys);
  const markers = resolveContextMarkersFromEnvelope(envelope);
  const moduleKeys = options?.effectiveModuleKeys;
  const entries = manifest.entries
    .map((e) => filterNavEntry(e, effective, markers, moduleKeys))
    .filter((e): e is NavigationEntry => e !== null);
  return { version: manifest.version, entries };
}
