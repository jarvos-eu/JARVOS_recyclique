/**
 * Story 27.4 — manifeste CREOS enrôlement terrain + bundle servi + widget enregistré.
 */
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { runtimeServedManifestLoadResult } from '../../src/app/demo/runtime-demo-manifest';
import { resolveWidget } from '../../src/registry';
import { parsePageManifestJson } from '../../src/validation/page-manifest-ingest';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '../../..');
const PAGE_PATH = join(REPO_ROOT, 'contracts/creos/manifests/page-transverse-shared-workstation-enroll.json');

describe('contracts/creos/manifests/page-transverse-shared-workstation-enroll.json (Story 27.4)', () => {
  it('parse sans erreur et résout le widget shared-workstation.enrollment', () => {
    const raw = readFileSync(PAGE_PATH, 'utf8');
    const { manifest, issues } = parsePageManifestJson(raw, 'page-transverse-shared-workstation-enroll.json');
    expect(issues, JSON.stringify(issues)).toHaveLength(0);
    expect(manifest?.pageKey).toBe('shared-workstation-enroll');
    const slot = manifest?.slots[0];
    expect(slot?.widgetType).toBe('shared-workstation.enrollment');
    const w = resolveWidget('shared-workstation.enrollment');
    expect(w.ok).toBe(true);
  });

  it('est chargé dans le bundle servi Peintre (route /shared-workstation/enroll)', () => {
    expect(runtimeServedManifestLoadResult.ok).toBe(true);
    if (!runtimeServedManifestLoadResult.ok) return;
    const page = runtimeServedManifestLoadResult.bundle.pages.find(
      (p) => p.pageKey === 'shared-workstation-enroll',
    );
    expect(page).toBeDefined();
    expect(page?.slots.some((s) => s.widgetType === 'shared-workstation.enrollment')).toBe(true);
  });

  it('n’apparaît pas dans la navigation transverse (écran setup ponctuel)', () => {
    expect(runtimeServedManifestLoadResult.ok).toBe(true);
    if (!runtimeServedManifestLoadResult.ok) return;
    const flat = runtimeServedManifestLoadResult.bundle.navigation.entries.flatMap(function walk(
      e,
    ): typeof runtimeServedManifestLoadResult.bundle.navigation.entries {
      return [e, ...(e.children?.flatMap(walk) ?? [])];
    });
    const pageKeys = flat.map((e) => e.pageKey).filter(Boolean);
    expect(pageKeys).not.toContain('shared-workstation-enroll');
  });
});
