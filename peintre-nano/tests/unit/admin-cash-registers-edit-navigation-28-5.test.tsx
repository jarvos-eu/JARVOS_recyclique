// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import type { ReactElement } from 'react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import type { AuthContextPort } from '../../src/app/auth/auth-context-port';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { AdminCashRegistersWidget } from '../../src/domains/admin-config/AdminCashRegistersWidget';
import type { CashRegisterAdminRowDto } from '../../src/api/admin-cash-registers-client';
import type { SiteAdminRowDto } from '../../src/api/admin-sites-client';
import '../../src/styles/tokens.css';

const siteId = '550e8400-e29b-41d4-a716-446655440001';
const siteId2 = '550e8400-e29b-41d4-a716-446655440003';
const registerId = '660e8400-e29b-41d4-a716-446655440002';

const siteRow: SiteAdminRowDto = {
  id: siteId,
  name: 'Recyclerie Pilote',
  city: 'Nantes',
  is_active: true,
  created_at: '2026-04-01T10:00:00.000Z',
  updated_at: '2026-04-01T10:00:00.000Z',
};

const siteRow2: SiteAdminRowDto = {
  id: siteId2,
  name: 'Site Secondaire',
  city: 'Angers',
  is_active: true,
  created_at: '2026-04-01T10:00:00.000Z',
  updated_at: '2026-04-01T10:00:00.000Z',
};

const registerRow: CashRegisterAdminRowDto = {
  id: registerId,
  name: 'Caisse 1',
  location: 'Accueil',
  site_id: siteId,
  is_active: true,
  workflow_options: {},
  enable_virtual: false,
  enable_deferred: false,
};

const { spaNavigateMock, listRegistersMock, listSitesMock, updateRegisterMock, getStatusMock } = vi.hoisted(
  () => ({
    spaNavigateMock: vi.fn(),
    listRegistersMock: vi.fn(),
    listSitesMock: vi.fn(),
    updateRegisterMock: vi.fn(),
    getStatusMock: vi.fn(),
  }),
);

vi.mock('../../src/app/demo/spa-navigate', () => ({
  spaNavigateTo: (path: string) => spaNavigateMock(path),
}));

vi.mock('../../src/api/admin-cash-registers-client', async (importOriginal) => {
  const mod = await importOriginal<typeof import('../../src/api/admin-cash-registers-client')>();
  return {
    ...mod,
    listCashRegistersForAdmin: (...args: unknown[]) => listRegistersMock(...args),
    updateCashRegisterForAdmin: (...args: unknown[]) => updateRegisterMock(...args),
    createCashRegisterForAdmin: vi.fn(),
    deleteCashRegisterForAdmin: vi.fn(),
  };
});

vi.mock('../../src/api/admin-sites-client', async (importOriginal) => {
  const mod = await importOriginal<typeof import('../../src/api/admin-sites-client')>();
  return {
    ...mod,
    listSitesForAdmin: (...args: unknown[]) => listSitesMock(...args),
  };
});

vi.mock('../../src/api/cash-session-client', () => ({
  getCashRegistersStatus: (...args: unknown[]) => getStatusMock(...args),
}));

function makeAuthStub(): AuthContextPort {
  return {
    getSession: () => ({ authenticated: true, userId: 'u1', userDisplayLabel: 'Test' }),
    getContextEnvelope: () => ({
      schemaVersion: '1',
      siteId,
      activeRegisterId: null,
      permissions: { permissionKeys: ['transverse.admin.view'] },
      issuedAt: Date.now(),
      runtimeStatus: 'ok',
    }),
    getAccessToken: () => 'tok',
  };
}

function wrap(ui: ReactElement) {
  return <RootProviders authAdapter={makeAuthStub()}>{ui}</RootProviders>;
}

describe('AdminCashRegistersWidget edit and navigation 28-5', () => {
  beforeAll(() => {
    globalThis.ResizeObserver = class {
      observe(): void {}
      unobserve(): void {}
      disconnect(): void {}
    } as typeof ResizeObserver;
    Element.prototype.scrollIntoView = vi.fn();
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  beforeEach(() => {
    spaNavigateMock.mockClear();
    updateRegisterMock.mockClear();
    listRegistersMock.mockResolvedValue({ ok: true, data: [registerRow] });
    listSitesMock.mockResolvedValue({ ok: true, data: [siteRow, siteRow2] });
    getStatusMock.mockResolvedValue({ ok: true, rows: [{ id: registerId, is_open: false }] });
    updateRegisterMock.mockResolvedValue({
      ok: true,
      register: {
        ...registerRow,
        name: 'Caisse principale',
        location: 'Hall',
        site_id: siteId,
      },
    });
  });

  afterEach(() => {
    cleanup();
  });

  it('affiche Recharger la liste et navigue vers le hub', async () => {
    render(wrap(<AdminCashRegistersWidget widgetId="registers" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Caisse 1')).toBeTruthy());

    expect(screen.getByTestId('admin-cash-registers-reload-list')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Recharger la liste' })).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Actualiser' })).toBeNull();

    fireEvent.click(screen.getByTestId('admin-cash-registers-back-to-hub'));
    expect(spaNavigateMock).toHaveBeenCalledWith('/admin/sites-and-registers');
  });

  it('recharge la liste (second appel API) et ferme la modal ouverte', async () => {
    render(wrap(<AdminCashRegistersWidget widgetId="registers" pageKey="test" />));
    await waitFor(() => expect(listRegistersMock.mock.calls.length).toBeGreaterThanOrEqual(1));
    const callsBeforeReload = listRegistersMock.mock.calls.length;

    fireEvent.click(screen.getByTestId(`admin-cash-registers-edit-${registerId}`));
    await screen.findByRole('dialog', { name: /Modifier le poste/i });

    fireEvent.click(screen.getByTestId('admin-cash-registers-reload-list'));
    await waitFor(() => expect(listRegistersMock.mock.calls.length).toBe(callsBeforeReload + 1));
    await waitFor(() => expect(screen.queryByRole('dialog', { name: /Modifier le poste/i })).toBeNull());
  });

  it('ouvre la modal Modifier, envoie PATCH nom/emplacement/site et met à jour la ligne', async () => {
    render(wrap(<AdminCashRegistersWidget widgetId="registers" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Caisse 1')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-cash-registers-edit-${registerId}`));
    const modal = await screen.findByTestId('admin-cash-registers-edit-modal');
    expect(within(modal).getByText('Modifier le poste')).toBeTruthy();

    fireEvent.change(within(modal).getByDisplayValue('Caisse 1'), { target: { value: 'Caisse principale' } });
    fireEvent.change(within(modal).getByDisplayValue('Accueil'), { target: { value: 'Hall' } });
    fireEvent.click(within(modal).getByTestId('admin-cash-registers-edit-submit'));

    await waitFor(() => {
      expect(updateRegisterMock).toHaveBeenCalledWith(
        expect.anything(),
        registerId,
        { name: 'Caisse principale', location: 'Hall', site_id: siteId },
      );
    });
    await waitFor(() => expect(screen.queryByRole('dialog', { name: /Modifier le poste/i })).toBeNull());
    await waitFor(() => expect(screen.getByText('Caisse principale')).toBeTruthy());
    expect(screen.getByText('Hall')).toBeTruthy();
  });

  it('change le site rattaché via Select et envoie PATCH', async () => {
    updateRegisterMock.mockResolvedValue({
      ok: true,
      register: { ...registerRow, site_id: siteId2 },
    });

    render(wrap(<AdminCashRegistersWidget widgetId="registers" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Caisse 1')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-cash-registers-edit-${registerId}`));
    const modal = await screen.findByTestId('admin-cash-registers-edit-modal');

    const siteInput = within(modal).getByTestId('admin-cash-registers-edit-site');
    fireEvent.focus(siteInput);
    fireEvent.keyDown(siteInput, { key: 'ArrowDown', code: 'ArrowDown' });
    fireEvent.keyDown(siteInput, { key: 'ArrowDown', code: 'ArrowDown' });
    fireEvent.keyDown(siteInput, { key: 'Enter', code: 'Enter' });
    fireEvent.click(within(modal).getByTestId('admin-cash-registers-edit-submit'));

    await waitFor(() => {
      expect(updateRegisterMock).toHaveBeenCalledWith(
        expect.anything(),
        registerId,
        { name: 'Caisse 1', location: 'Accueil', site_id: siteId2 },
      );
    });
  });

  it('affiche une alerte et garde la modal ouverte si le PATCH échoue', async () => {
    updateRegisterMock.mockResolvedValue({
      ok: false,
      status: 409,
      detail: 'Session ouverte sur ce poste',
    });

    render(wrap(<AdminCashRegistersWidget widgetId="registers" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Caisse 1')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-cash-registers-edit-${registerId}`));
    const modal = await screen.findByTestId('admin-cash-registers-edit-modal');
    fireEvent.click(within(modal).getByTestId('admin-cash-registers-edit-submit'));

    await waitFor(() => expect(screen.getByTestId('cashflow-submit-error')).toBeTruthy());
    expect(screen.getByText(/Session ouverte sur ce poste/)).toBeTruthy();
    expect(screen.getByTestId('admin-cash-registers-edit-modal')).toBeTruthy();
  });

  it('détache le site rattaché (site_id null) via Select', async () => {
    updateRegisterMock.mockResolvedValue({
      ok: true,
      register: { ...registerRow, site_id: null },
    });

    render(wrap(<AdminCashRegistersWidget widgetId="registers" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Caisse 1')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-cash-registers-edit-${registerId}`));
    const modal = await screen.findByTestId('admin-cash-registers-edit-modal');

    const siteInput = within(modal).getByTestId('admin-cash-registers-edit-site');
    fireEvent.focus(siteInput);
    fireEvent.keyDown(siteInput, { key: 'ArrowDown', code: 'ArrowDown' });
    fireEvent.keyDown(siteInput, { key: 'Enter', code: 'Enter' });
    fireEvent.click(within(modal).getByTestId('admin-cash-registers-edit-submit'));

    await waitFor(() => {
      expect(updateRegisterMock).toHaveBeenCalledWith(
        expect.anything(),
        registerId,
        { name: 'Caisse 1', location: 'Accueil', site_id: null },
      );
    });
  });

  it('bascule is_active via switch inline', async () => {
    updateRegisterMock.mockResolvedValue({
      ok: true,
      register: { ...registerRow, is_active: false },
    });

    render(wrap(<AdminCashRegistersWidget widgetId="registers" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Caisse 1')).toBeTruthy());

    fireEvent.click(screen.getByLabelText('Poste Caisse 1 actif'));

    await waitFor(() => {
      expect(updateRegisterMock).toHaveBeenCalledWith(expect.anything(), registerId, { is_active: false });
    });
  });

  it('désactive Enregistrer et n’envoie pas PATCH si le nom est vide', async () => {
    render(wrap(<AdminCashRegistersWidget widgetId="registers" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Caisse 1')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-cash-registers-edit-${registerId}`));
    const modal = await screen.findByTestId('admin-cash-registers-edit-modal');
    fireEvent.change(within(modal).getByDisplayValue('Caisse 1'), { target: { value: '' } });

    const submit = within(modal).getByTestId('admin-cash-registers-edit-submit');
    expect(submit).toHaveProperty('disabled', true);
    fireEvent.click(submit);
    expect(updateRegisterMock).not.toHaveBeenCalled();
  });

  it('désactive Recharger la liste et Modifier pendant un PATCH lent (editBusy)', async () => {
    let resolveEdit: (value: { ok: true; register: CashRegisterAdminRowDto }) => void;
    updateRegisterMock.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveEdit = resolve;
        }),
    );

    render(wrap(<AdminCashRegistersWidget widgetId="registers" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Caisse 1')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-cash-registers-edit-${registerId}`));
    const modal = await screen.findByTestId('admin-cash-registers-edit-modal');
    fireEvent.click(within(modal).getByTestId('admin-cash-registers-edit-submit'));

    await waitFor(() => {
      expect(screen.getByTestId('admin-cash-registers-reload-list')).toHaveProperty('disabled', true);
    });
    expect(screen.getByTestId(`admin-cash-registers-edit-${registerId}`)).toHaveProperty('disabled', true);

    resolveEdit!({ ok: true, register: { ...registerRow, name: 'Caisse principale' } });
    await waitFor(() => {
      expect(screen.getByTestId('admin-cash-registers-reload-list')).toHaveProperty('disabled', false);
    });
  });

  it('désactive Supprimer sur la ligne dont la modal d’édition est ouverte', async () => {
    render(wrap(<AdminCashRegistersWidget widgetId="registers" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Caisse 1')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-cash-registers-edit-${registerId}`));
    await screen.findByTestId('admin-cash-registers-edit-modal');

    const deleteBtn = screen.getByRole('button', { name: 'Supprimer' });
    expect(deleteBtn).toHaveProperty('disabled', true);
  });
});
