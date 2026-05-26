import { describe, expect, it } from 'vitest';
import {
  buildKpiLiveBannerModuleDocument,
  parseEtagFromResponse,
  parseEtagVersion,
  parseKpiLiveBannerPayload,
  parseModuleConfigDocument,
} from '../../src/api/module-config-client';

describe('module-config-client', () => {
  it('parse ETag et version', () => {
    expect(parseEtagVersion('W/"3"')).toBe(3);
    expect(parseEtagVersion('"12"')).toBe(12);
    expect(parseEtagVersion(null)).toBeNull();
    const res = new Response('{}', { headers: { ETag: 'W/"1"' } });
    expect(parseEtagFromResponse(res)).toBe('W/"1"');
  });

  it('parse document et payload kpi-live-banner', () => {
    const doc = parseModuleConfigDocument({
      schema_version: '1.0.0',
      payload: {
        show_on_caisse: true,
        show_on_reception: false,
        refresh_interval_seconds: 30,
      },
      version: 2,
    });
    expect(doc?.version).toBe(2);
    const payload = parseKpiLiveBannerPayload(doc!.payload);
    expect(payload?.show_on_reception).toBe(false);
  });

  it('build document module', () => {
    const doc = buildKpiLiveBannerModuleDocument({
      show_on_caisse: true,
      show_on_reception: true,
      refresh_interval_seconds: 60,
    });
    expect(doc.schema_version).toBe('1.0.0');
    expect(doc.payload.refresh_interval_seconds).toBe(60);
  });
});
