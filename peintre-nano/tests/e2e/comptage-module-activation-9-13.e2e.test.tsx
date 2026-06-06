// @vitest-environment jsdom

import '@mantine/core/styles.css';

import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';

import type { ReactElement } from 'react';

import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';

import type { AuthContextPort } from '../../src/app/auth/auth-context-port';

import { DEMO_AUTH_STUB_SITE_ID } from '../../src/app/auth/default-demo-auth-adapter';

import { RootProviders } from '../../src/app/providers/RootProviders';

import {

  COMPTAGE_PIECES_BILLETS_MODULE_KEY,

} from '../../src/api/comptage-module-config';

import {

  KPI_LIVE_BANNER_MODULE_KEY,

  KPI_LIVE_BANNER_SCHEMA_VERSION,

} from '../../src/api/module-config-client';

import { AdminModulesWidget } from '../../src/domains/admin-config/AdminModulesWidget';

import { CashflowCloseWizard } from '../../src/domains/cashflow/CashflowCloseWizard';

import '../../src/registry';

import '../../src/styles/tokens.css';

import {

  comptageModuleDisabledJson,

  comptageModulePilotJson,

  denominationCountResponseForTotal,

  FIXTURE_CASH_DENOMINATIONS,

} from '../unit/fixtures/cash-denominations-api';



const SESSION_ID = '00000000-0000-4000-8000-000000000099';

const siteId = DEMO_AUTH_STUB_SITE_ID;



function requestUrl(input: RequestInfo | URL): string {

  if (typeof input === 'string') return input;

  if (input instanceof URL) return input.href;

  return input.url;

}



function mockFetchResponse(body: unknown, ok = true, status = 200, etag?: string) {

  const headers: Record<string, string> = {};

  if (etag) headers.ETag = etag;

  return {

    ok,

    status,

    headers: { get: (k: string) => headers[k] ?? null },

    text: async () => (typeof body === 'string' ? body : JSON.stringify(body)),

  };

}



function sessionJson() {

  return {

    id: SESSION_ID,

    operator_id: 'op1',

    site_id: siteId,

    initial_amount: 50,

    current_amount: 75,

    status: 'open',

    opened_at: '2026-01-01T00:00:00Z',

    total_sales: 25,

    total_donations: 0,

    total_weight_out: 0,

    totals: { sales_completed: 25, refunds: 0, net: 25 },

    closing_preview_theoretical_amount: 75,

  };

}



const kpiDefaultDoc = {

  schema_version: KPI_LIVE_BANNER_SCHEMA_VERSION,

  payload: {

    show_on_caisse: true,

    show_on_reception: true,

    refresh_interval_seconds: 60,

  },

  version: 0,

};



function makeAdminAuthStub(): AuthContextPort {

  return {

    getSession: () => ({ authenticated: true, userId: 'u1', userDisplayLabel: 'Test' }),

    getContextEnvelope: () => ({

      schemaVersion: '1',

      siteId,

      activeRegisterId: null,

      permissions: { permissionKeys: ['transverse.admin.view', 'caisse.sale_correct'] },

      issuedAt: Date.now(),

      runtimeStatus: 'ok',

    }),

    getAccessToken: () => 'tok',

  };

}



function wrapAdmin(ui: ReactElement) {

  return <RootProviders authAdapter={makeAdminAuthStub()}>{ui}</RootProviders>;

}



function buildWizardFetchMock(comptageDoc: ReturnType<typeof comptageModuleDisabledJson>) {

  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {

    const url = requestUrl(input);

    const method = (init?.method ?? 'GET').toUpperCase();



    if (url.includes('/v1/cash-sessions/current')) {

      return Promise.resolve(mockFetchResponse(sessionJson()));

    }



    if (url.includes(`/module-config/${COMPTAGE_PIECES_BILLETS_MODULE_KEY}`)) {

      return Promise.resolve(mockFetchResponse(comptageDoc, true, 200, 'W/"0"'));

    }



    if (url.includes('/v1/cash-denominations')) {

      return Promise.resolve(mockFetchResponse(FIXTURE_CASH_DENOMINATIONS));

    }



    if (url.includes('/denomination-count')) {

      return Promise.resolve(mockFetchResponse(denominationCountResponseForTotal(7500)));

    }



    if (method === 'POST' && url.includes('/close')) {

      return Promise.resolve(

        mockFetchResponse({

          id: SESSION_ID,

          status: 'closed',

          anomaly_close_sheet: false,

          close_sheet_pdf_url: null,

        }),

      );

    }



    return Promise.resolve(mockFetchResponse({}));

  });

}



beforeAll(() => {

  Object.defineProperty(window, 'matchMedia', {

    writable: true,

    configurable: true,

    value: (query: string) => ({

      matches: false,

      media: query,

      onchange: null,

      addListener: () => {},

      removeListener: () => {},

      addEventListener: () => {},

      removeEventListener: () => {},

      dispatchEvent: () => false,

    }),

  });

});



describe('E2E — activation module comptage (Story 9.13)', () => {

  beforeEach(() => {

    vi.stubGlobal(

      'ResizeObserver',

      class {

        observe(): void {}

        unobserve(): void {}

        disconnect(): void {}

      },

    );

  });



  afterEach(() => {

    window.history.pushState({}, '', '/');

    vi.unstubAllGlobals();

    vi.restoreAllMocks();

    cleanup();

  });



  describe('Q-HITL-09 — module off (parité legacy)', () => {

    it('wizard : enabled false → actual_amount, pas de grille ni PUT denomination-count', async () => {

      const fetchMock = buildWizardFetchMock(comptageModuleDisabledJson());

      vi.stubGlobal('fetch', fetchMock);



      render(

        <RootProviders disableUserPrefsPersistence>

          <CashflowCloseWizard widgetProps={{}} />

        </RootProviders>,

      );



      await waitFor(() => expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy());

      expect(screen.getByRole('button', { name: /Continuer vers le comptage$/i })).toBeTruthy();

      expect(screen.queryByRole('button', { name: /Continuer vers le comptage grille/i })).toBeNull();



      fireEvent.click(screen.getByRole('button', { name: /Continuer vers le comptage$/i }));

      expect(screen.getByTestId('cashflow-close-actual-amount')).toBeTruthy();

      expect(screen.queryByTestId('cashflow-denomination-grid')).toBeNull();



      fireEvent.click(screen.getByRole('button', { name: /Continuer vers le PIN/i }));

      await waitFor(() => expect(screen.getByTestId('cashflow-close-pin')).toBeTruthy());



      fireEvent.change(screen.getByLabelText(/PIN step-up/i), { target: { value: '1234' } });

      fireEvent.click(screen.getByTestId('cashflow-close-submit'));



      await waitFor(() => expect(screen.getByTestId('cashflow-close-success')).toBeTruthy());



      const putCalls = fetchMock.mock.calls.filter(

        (c) => requestUrl(c[0]).includes('/denomination-count') && (c[1]?.method ?? 'GET').toUpperCase() === 'PUT',

      );

      expect(putCalls.length).toBe(0);

    });

  });



  describe('Q-HITL-11 — module on (config pilote)', () => {

    it('wizard : config pilote → grille obligatoire, pas de saisie legacy actual_amount', async () => {

      const fetchMock = buildWizardFetchMock(comptageModulePilotJson());

      vi.stubGlobal('fetch', fetchMock);



      render(

        <RootProviders disableUserPrefsPersistence>

          <CashflowCloseWizard widgetProps={{}} />

        </RootProviders>,

      );



      await waitFor(() => expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy());

      expect(screen.getByRole('button', { name: /Continuer vers le comptage grille/i })).toBeTruthy();



      fireEvent.click(screen.getByRole('button', { name: /Continuer vers le comptage grille/i }));

      await waitFor(() => expect(screen.getByTestId('cashflow-denomination-grid')).toBeTruthy());



      expect(screen.getByTestId('cashflow-denomination-rules')).toBeTruthy();

      expect(screen.queryByTestId('cashflow-close-actual-amount')).toBeNull();

      expect(screen.queryByRole('button', { name: /passer/i })).toBeNull();

    });



    it('show_images false masque les pictos mais conserve la grille', async () => {

      const fetchMock = buildWizardFetchMock(comptageModulePilotJson(false));

      vi.stubGlobal('fetch', fetchMock);



      render(

        <RootProviders disableUserPrefsPersistence>

          <CashflowCloseWizard widgetProps={{}} />

        </RootProviders>,

      );



      await waitFor(() => expect(screen.getByTestId('cashflow-close-recap')).toBeTruthy());

      fireEvent.click(screen.getByRole('button', { name: /Continuer vers le comptage grille/i }));

      await waitFor(() => expect(screen.getByTestId('cashflow-denomination-grid')).toBeTruthy());



      expect(screen.getByTestId('cashflow-denom-row-EUR_20000')).toBeTruthy();

      expect(screen.queryByTestId('cashflow-denom-picto-EUR_20000')).toBeNull();

    });

  });



  describe('Admin /admin/modules — activation et rollback', () => {

    it('active le module pilote via PATCH (4 toggles) puis reflète le serveur', async () => {

      let comptageDoc = comptageModuleDisabledJson();

      const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {

        const url = requestUrl(input);

        const method = (init?.method ?? 'GET').toUpperCase();



        if (url.includes(`/module-config/${KPI_LIVE_BANNER_MODULE_KEY}`) && method === 'GET') {

          return mockFetchResponse(kpiDefaultDoc, true, 200, 'W/"0"');

        }



        if (url.includes(`/module-config/${COMPTAGE_PIECES_BILLETS_MODULE_KEY}`) && method === 'GET') {

          return mockFetchResponse(comptageDoc, true, 200, `W/"${comptageDoc.version}"`);

        }



        if (url.includes(`/module-config/${COMPTAGE_PIECES_BILLETS_MODULE_KEY}`) && method === 'PATCH') {

          const body = JSON.parse(String(init?.body)) as typeof comptageDoc;

          expect(body.payload).toEqual(comptageModulePilotJson().payload);

          comptageDoc = { ...comptageModulePilotJson(), version: 1 };

          return mockFetchResponse(comptageDoc, true, 200, 'W/"1"');

        }



        return mockFetchResponse({}, false, 404);

      });

      vi.stubGlobal('fetch', fetchMock);



      render(wrapAdmin(<AdminModulesWidget />));



      await waitFor(() => expect(screen.getByTestId('comptage-pieces-billets-module-panel')).toBeTruthy());



      fireEvent.click(screen.getByTestId('admin-comptage-toggle-enabled'));

      fireEvent.click(screen.getByTestId('admin-comptage-toggle-skip-allowed'));

      fireEvent.click(screen.getByTestId('admin-comptage-toggle-require-grid'));

      fireEvent.click(screen.getByTestId('admin-comptage-save'));



      await waitFor(() => expect(screen.getByTestId('admin-comptage-save-success')).toBeTruthy());



      const patchCall = fetchMock.mock.calls.find(

        (c) =>

          requestUrl(c[0]).includes(`/module-config/${COMPTAGE_PIECES_BILLETS_MODULE_KEY}`) &&

          (c[1]?.method ?? 'GET').toUpperCase() === 'PATCH',

      );

      expect(patchCall).toBeTruthy();

    });



    it('rollback : désactive le module (enabled false) via admin PATCH', async () => {

      let comptageDoc = comptageModulePilotJson();

      const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {

        const url = requestUrl(input);

        const method = (init?.method ?? 'GET').toUpperCase();



        if (url.includes(`/module-config/${KPI_LIVE_BANNER_MODULE_KEY}`) && method === 'GET') {

          return mockFetchResponse(kpiDefaultDoc, true, 200, 'W/"0"');

        }



        if (url.includes(`/module-config/${COMPTAGE_PIECES_BILLETS_MODULE_KEY}`) && method === 'GET') {

          return mockFetchResponse(comptageDoc, true, 200, `W/"${comptageDoc.version}"`);

        }



        if (url.includes(`/module-config/${COMPTAGE_PIECES_BILLETS_MODULE_KEY}`) && method === 'PATCH') {

          const body = JSON.parse(String(init?.body)) as typeof comptageDoc;

          expect(body.payload.enabled).toBe(false);

          comptageDoc = { ...comptageModuleDisabledJson(), version: 2 };

          return mockFetchResponse(comptageDoc, true, 200, 'W/"2"');

        }



        return mockFetchResponse({}, false, 404);

      });

      vi.stubGlobal('fetch', fetchMock);



      render(wrapAdmin(<AdminModulesWidget />));



      await waitFor(() => expect(screen.getByTestId('admin-comptage-toggle-enabled')).toBeTruthy());



      fireEvent.click(screen.getByTestId('admin-comptage-toggle-enabled'));

      fireEvent.click(screen.getByTestId('admin-comptage-save'));



      await waitFor(() => expect(screen.getByTestId('admin-comptage-save-success')).toBeTruthy());

    });

  });

});


