import fs from 'node:fs';
import react from '@vitejs/plugin-react';
import { defineConfig, searchForWorkspaceRoot } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

const runningInContainer = fs.existsSync('/.dockerenv') || fs.existsSync('/run/.containerenv');
const devProxyTarget =
  process.env.PEINTRE_DEV_PROXY_TARGET ||
  process.env.DEV_PROXY_TARGET ||
  process.env.VITE_DEV_PROXY_TARGET ||
  (runningInContainer ? 'http://api:8000' : 'http://localhost:8000');

/** Préfixe API same-origin (proxy Vite dev + prod) — denylist SW navigateFallback. */
const recycliqueApiPrefix = process.env.VITE_RECYCLIQUE_API_PREFIX ?? '/api';
const apiPathDenyPattern = new RegExp(
  `^${recycliqueApiPrefix.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`,
);

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: 'auto',
      includeAssets: ['icons/icon-192.png', 'icons/icon-512.png', 'vite.svg'],
      manifest: {
        name: 'Recyclique',
        short_name: 'Recyclique',
        description:
          'Poste partagé connecté — actions métier sur le réseau uniquement.',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        orientation: 'any',
        lang: 'fr',
        theme_color: '#228be6',
        background_color: '#f8f9fa',
        icons: [
          {
            src: '/icons/icon-192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any',
          },
          {
            src: '/icons/icon-192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'maskable',
          },
          {
            src: '/icons/icon-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any',
          },
          {
            src: '/icons/icon-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        navigateFallback: 'index.html',
        navigateFallbackDenylist: [apiPathDenyPattern, /^\/api/],
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        globIgnores: ['**/manifests/**', 'manifests/**'],
        runtimeCaching: [],
        cleanupOutdatedCaches: true,
      },
      devOptions: {
        enabled: false,
      },
    }),
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    fs: {
      // Docker dev mounts CREOS contracts outside `/app`; keep served manifests reachable.
      allow: [searchForWorkspaceRoot(process.cwd()), '/contracts'],
    },
    proxy: {
      // Same-origin API calls in dev: host mode defaults to localhost, Docker frontend overrides to `api:8000`.
      '/api': {
        target: devProxyTarget,
        changeOrigin: false,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
