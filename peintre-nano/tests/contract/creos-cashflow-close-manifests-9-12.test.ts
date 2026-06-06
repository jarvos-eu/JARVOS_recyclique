import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { parse as parseYaml } from 'yaml';

const REPO_ROOT = resolve(import.meta.dirname, '../../..');

function readJson(rel: string): unknown {
  return JSON.parse(readFileSync(resolve(REPO_ROOT, rel), 'utf8'));
}

describe('CREOS — cashflow-close manifests (Story 9.12)', () => {
  it('widgets-catalog expose les operation_id OpenAPI du wizard comptage', () => {
    const catalog = readJson('contracts/creos/manifests/widgets-catalog-cashflow-close.json') as {
      widgets: Array<{ type: string; data_contract?: { operation_id?: string; panel_operations?: Array<{ operation_id: string }> } }>;
    };
    const wizard = catalog.widgets.find((w) => w.type === 'cashflow-close-wizard');
    expect(wizard?.data_contract?.operation_id).toBe('recyclique_cashSessions_getCurrentOpenSession');
    const panelOps = wizard?.data_contract?.panel_operations ?? [];
    const ids = panelOps.map((p) => p.operation_id);
    expect(ids).toContain('recyclique_cashSessions_upsertDenominationCount');
    expect(ids).toContain('recyclique_cashSessions_getDenominationCount');
    expect(ids).toContain('recyclique_cashSessions_closeSession');
  });

  it('page-cashflow-close mentionne le module optionnel comptage', () => {
    const page = readJson('contracts/creos/manifests/page-cashflow-close.json') as {
      slots: Array<{ widget_props?: { optional_module_key?: string } }>;
    };
    const main = page.slots.find((s) => s.widget_props?.optional_module_key);
    expect(main?.widget_props?.optional_module_key).toBe('comptage-pieces-billets');
  });

  it('operationId upsertDenominationCount présent dans OpenAPI', () => {
    const yaml = readFileSync(resolve(REPO_ROOT, 'contracts/openapi/recyclique-api.yaml'), 'utf8');
    const doc = parseYaml(yaml) as { paths?: Record<string, unknown> };
    const paths = Object.keys(doc.paths ?? {}).join('\n');
    expect(paths).toMatch(/denomination-count/);
    const raw = yaml;
    expect(raw).toMatch(/recyclique_cashSessions_upsertDenominationCount/);
    expect(raw).toMatch(/recyclique_cashSessions_getDenominationCount/);
  });
});
