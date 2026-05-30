import { readFileSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { describe, expect, it } from 'vitest';

const projectRoot = resolve(import.meta.dirname, '../..');
const manifestPath = join(projectRoot, 'public/manifest.webmanifest');
const indexHtmlPath = join(projectRoot, 'index.html');
const icon192Path = join(projectRoot, 'public/icons/icon-192.png');
const icon512Path = join(projectRoot, 'public/icons/icon-512.png');
const viteConfigPath = join(projectRoot, 'vite.config.ts');
const pwaDocPath = join(projectRoot, 'docs/pwa-terrain.md');

type WebManifest = {
  name: string;
  short_name: string;
  display: string;
  start_url: string;
  icons: Array<{ sizes: string; src: string; purpose?: string }>;
};

function loadManifest(): WebManifest {
  return JSON.parse(readFileSync(manifestPath, 'utf8')) as WebManifest;
}

describe('PWA manifest (story 27.5)', () => {
  it('expose un manifest.webmanifest valide avec champs installables', () => {
    expect(existsSync(manifestPath)).toBe(true);
    const manifest = loadManifest();
    expect(manifest.name).toBe('Recyclique');
    expect(manifest.short_name).toBe('Recyclique');
    expect(manifest.display).toBe('standalone');
    expect(manifest.start_url).toBe('/');
    expect(manifest.icons.length).toBeGreaterThanOrEqual(2);
    const sizes = manifest.icons.map((i) => i.sizes);
    expect(sizes).toContain('192x192');
    expect(sizes).toContain('512x512');
  });

  it('déclare des icônes PNG présentes sur disque', () => {
    expect(existsSync(icon192Path)).toBe(true);
    expect(existsSync(icon512Path)).toBe(true);
  });

  it('lie le manifeste dans index.html', () => {
    const html = readFileSync(indexHtmlPath, 'utf8');
    expect(html).toMatch(/rel="manifest"/);
    expect(html).toContain('/manifest.webmanifest');
    expect(html).toContain('name="theme-color"');
    expect(html).toContain('Recyclique');
  });

  it('configure Workbox sans cache runtime API (vite.config)', () => {
    const config = readFileSync(viteConfigPath, 'utf8');
    expect(config).toContain('navigateFallbackDenylist');
    expect(config).toContain('runtimeCaching: []');
    expect(config).toContain('globIgnores');
    expect(config).toContain('manifests/**');
    expect(config).not.toMatch(/runtimeCaching:\s*\[[\s\S]*?urlPattern[\s\S]*?\/api/);
  });

  it('documente installable ≠ offline pour le terrain', () => {
    expect(existsSync(pwaDocPath)).toBe(true);
    const doc = readFileSync(pwaDocPath, 'utf8');
    expect(doc.toLowerCase()).toContain('installable');
    expect(doc.toLowerCase()).toMatch(/hors ligne|offline/);
    expect(doc).toMatch(/IndexedDB|identité poste/i);
  });

  it('le SW buildé denylist /api sans runtimeCaching métier (si dist présent)', () => {
    const swPath = join(projectRoot, 'dist/sw.js');
    if (!existsSync(swPath)) {
      return;
    }
    const sw = readFileSync(swPath, 'utf8');
    expect(sw).toMatch(/denylist:\[[\s\S]*?\\\/api/);
    expect(sw).not.toMatch(/NetworkFirst|StaleWhileRevalidate/);
    expect(sw).not.toContain('manifests/navigation');
    expect(sw).not.toMatch(/runtimeCaching/i);
  });
});
