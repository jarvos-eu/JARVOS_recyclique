// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import type { ReactElement } from 'react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import type { AuthContextPort } from '../../src/app/auth/auth-context-port';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { AdminSitesAndRegistersHubWidget } from '../../src/domains/admin-config/AdminSitesAndRegistersHubWidget';
import { AdminSitesWidget } from '../../src/domains/admin-config/AdminSitesWidget';
import type { SiteAdminRowDto } from '../../src/api/admin-sites-client';
import '../../src/styles/tokens.css';

const siteId = '550e8400-e29b-41d4-a716-446655440001';

const siteRow: SiteAdminRowDto = {
  id: siteId,
  name: 'Recyclerie Pilote',
  city: 'Nantes',
  is_active: true,
  created_at: '2026-04-01T10:00:00.000Z',
  updated_at: '2026-04-01T10:00:00.000Z',
};

const { spaNavigateMock, listSitesMock, updateSiteMock } = vi.hoisted(() => ({
  spaNavigateMock: vi.fn(),
  listSitesMock: vi.fn(),
  updateSiteMock: vi.fn(),
}));

vi.mock('../../src/app/demo/spa-navigate', () => ({
  spaNavigateTo: (path: string) => spaNavigateMock(path),
}));

vi.mock('../../src/api/admin-sites-client', async (importOriginal) => {
  const mod = await importOriginal<typeof import('../../src/api/admin-sites-client')>();
  return {
    ...mod,
    listSitesForAdmin: (...args: unknown[]) => listSitesMock(...args),
    updateSiteForAdmin: (...args: unknown[]) => updateSiteMock(...args),
    createSiteForAdmin: vi.fn(),
    deleteSiteForAdmin: vi.fn(),
  };
});

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

describe('AdminSitesAndRegistersHubWidget 28-5', () => {
  beforeAll(() => {
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
  });

  afterEach(() => {
    cleanup();
  });

  it('n’affiche plus le bandeau gris central et garde les testid hub', () => {
    render(wrap(<AdminSitesAndRegistersHubWidget widgetId="hub" pageKey="test" />));
    expect(screen.getByTestId('admin-sites-and-registers-hub')).toBeTruthy();
    expect(screen.queryByText(/Choisissez l/)).toBeNull();
    expect(screen.getByTestId('admin-sites-and-registers-nav-sites')).toBeTruthy();
    expect(screen.getByTestId('admin-sites-and-registers-nav-cash-registers')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Gérer les sites' })).toBeTruthy();
    expect(screen.queryByText('Sites de collecte et paramètres associés')).toBeNull();
  });

  it('affiche Retour au tableau de bord et navigue vers sites ou postes', () => {
    render(wrap(<AdminSitesAndRegistersHubWidget widgetId="hub" pageKey="test" />));
    expect(screen.getByTestId('admin-sites-and-registers-back-dashboard')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Retour au tableau de bord' })).toBeTruthy();

    fireEvent.click(screen.getByTestId('admin-sites-and-registers-nav-sites'));
    expect(spaNavigateMock).toHaveBeenCalledWith('/admin/sites');

    spaNavigateMock.mockClear();
    fireEvent.click(screen.getByTestId('admin-sites-and-registers-nav-cash-registers'));
    expect(spaNavigateMock).toHaveBeenCalledWith('/admin/cash-registers');
  });

  it('navigue vers le tableau de bord admin au clic Retour', () => {
    render(wrap(<AdminSitesAndRegistersHubWidget widgetId="hub" pageKey="test" />));
    fireEvent.click(screen.getByTestId('admin-sites-and-registers-back-dashboard'));
    expect(spaNavigateMock).toHaveBeenCalledWith('/admin');
  });
});

describe('AdminSitesWidget edit and navigation 28-5', () => {
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
    updateSiteMock.mockClear();
    listSitesMock.mockResolvedValue({ ok: true, data: [siteRow] });
    updateSiteMock.mockResolvedValue({
      ok: true,
      site: { ...siteRow, name: 'Recyclerie Renommée', city: 'Angers' },
    });
  });

  afterEach(() => {
    cleanup();
  });

  it('affiche Recharger la liste et navigue vers le hub', async () => {
    render(wrap(<AdminSitesWidget widgetId="sites" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Recyclerie Pilote')).toBeTruthy());

    expect(screen.getByTestId('admin-sites-reload-list')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Recharger la liste' })).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Actualiser' })).toBeNull();

    fireEvent.click(screen.getByTestId('admin-sites-back-to-hub'));
    expect(spaNavigateMock).toHaveBeenCalledWith('/admin/sites-and-registers');
  });

  it('recharge la liste (second appel API) et ferme la modal ouverte', async () => {
    render(wrap(<AdminSitesWidget widgetId="sites" pageKey="test" />));
    await waitFor(() => expect(listSitesMock.mock.calls.length).toBeGreaterThanOrEqual(1));
    const callsBeforeReload = listSitesMock.mock.calls.length;

    fireEvent.click(screen.getByTestId(`admin-sites-edit-${siteId}`));
    await screen.findByRole('dialog', { name: /Modifier le site/i });

    fireEvent.click(screen.getByTestId('admin-sites-reload-list'));
    await waitFor(() => expect(listSitesMock.mock.calls.length).toBe(callsBeforeReload + 1));
    await waitFor(() => expect(screen.queryByRole('dialog', { name: /Modifier le site/i })).toBeNull());
  });

  it('ouvre la modal Modifier, envoie PATCH nom/ville et met à jour la ligne', async () => {
    render(wrap(<AdminSitesWidget widgetId="sites" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Recyclerie Pilote')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-sites-edit-${siteId}`));
    const modal = await screen.findByTestId('admin-sites-edit-modal');
    expect(within(modal).getByText('Modifier le site')).toBeTruthy();

    const nameInput = within(modal).getByDisplayValue('Recyclerie Pilote');
    const cityInput = within(modal).getByDisplayValue('Nantes');
    fireEvent.change(nameInput, { target: { value: 'Recyclerie Renommée' } });
    fireEvent.change(cityInput, { target: { value: 'Angers' } });
    fireEvent.click(within(modal).getByTestId('admin-sites-edit-submit'));

    await waitFor(() => {
      expect(updateSiteMock).toHaveBeenCalledWith(
        expect.anything(),
        siteId,
        { name: 'Recyclerie Renommée', city: 'Angers' },
      );
    });
    await waitFor(() => expect(screen.queryByRole('dialog', { name: /Modifier le site/i })).toBeNull());
    await waitFor(() => expect(screen.getByText('Recyclerie Renommée')).toBeTruthy());
    expect(screen.getByText('Angers')).toBeTruthy();
  });

  it('envoie city null quand la ville est vidée', async () => {
    updateSiteMock.mockResolvedValue({
      ok: true,
      site: { ...siteRow, city: null },
    });

    render(wrap(<AdminSitesWidget widgetId="sites" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Recyclerie Pilote')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-sites-edit-${siteId}`));
    const modal = await screen.findByTestId('admin-sites-edit-modal');
    fireEvent.change(within(modal).getByDisplayValue('Nantes'), { target: { value: '' } });
    fireEvent.click(within(modal).getByTestId('admin-sites-edit-submit'));

    await waitFor(() => {
      expect(updateSiteMock).toHaveBeenCalledWith(
        expect.anything(),
        siteId,
        { name: 'Recyclerie Pilote', city: null },
      );
    });
  });

  it('affiche une alerte et garde la modal ouverte si le PATCH échoue', async () => {
    updateSiteMock.mockResolvedValue({
      ok: false,
      status: 409,
      detail: 'Site lié à des postes actifs',
    });

    render(wrap(<AdminSitesWidget widgetId="sites" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Recyclerie Pilote')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-sites-edit-${siteId}`));
    const modal = await screen.findByTestId('admin-sites-edit-modal');
    fireEvent.click(within(modal).getByTestId('admin-sites-edit-submit'));

    await waitFor(() => expect(screen.getByTestId('cashflow-submit-error')).toBeTruthy());
    expect(screen.getByText(/Site lié à des postes actifs/)).toBeTruthy();
    expect(screen.getByTestId('admin-sites-edit-modal')).toBeTruthy();
  });

  it('désactive Modifier et Supprimer pendant le toggle actif/inactif', async () => {
    let resolveToggle: (value: { ok: true; site: SiteAdminRowDto }) => void;
    updateSiteMock.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveToggle = resolve;
        }),
    );

    render(wrap(<AdminSitesWidget widgetId="sites" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Recyclerie Pilote')).toBeTruthy());

    const toggle = screen.getByRole('switch', { name: /Site Recyclerie Pilote actif/i });
    fireEvent.click(toggle);

    await waitFor(() => {
      expect(screen.getByTestId(`admin-sites-edit-${siteId}`)).toHaveProperty('disabled', true);
    });
    const deleteBtn = screen.getByRole('button', { name: 'Supprimer' });
    expect(deleteBtn).toHaveProperty('disabled', true);

    resolveToggle!({ ok: true, site: { ...siteRow, is_active: false } });
    await waitFor(() => {
      expect(screen.getByTestId(`admin-sites-edit-${siteId}`)).toHaveProperty('disabled', false);
    });
  });

  it('bascule is_active via switch inline', async () => {
    updateSiteMock.mockResolvedValue({
      ok: true,
      site: { ...siteRow, is_active: false },
    });

    render(wrap(<AdminSitesWidget widgetId="sites" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Recyclerie Pilote')).toBeTruthy());

    fireEvent.click(screen.getByLabelText('Site Recyclerie Pilote actif'));

    await waitFor(() => {
      expect(updateSiteMock).toHaveBeenCalledWith(expect.anything(), siteId, { is_active: false });
    });
  });

  it('désactive le switch actif/inactif sur la ligne en cours d’édition', async () => {
    render(wrap(<AdminSitesWidget widgetId="sites" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Recyclerie Pilote')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-sites-edit-${siteId}`));
    await screen.findByTestId('admin-sites-edit-modal');

    const toggle = screen.getByRole('switch', { name: /Site Recyclerie Pilote actif/i });
    expect(toggle).toHaveProperty('disabled', true);
  });

  it('désactive Recharger la liste pendant un PATCH lent (editBusy)', async () => {
    let resolveEdit: (value: { ok: true; site: SiteAdminRowDto }) => void;
    updateSiteMock.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveEdit = resolve;
        }),
    );

    render(wrap(<AdminSitesWidget widgetId="sites" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Recyclerie Pilote')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-sites-edit-${siteId}`));
    const modal = await screen.findByTestId('admin-sites-edit-modal');
    fireEvent.click(within(modal).getByTestId('admin-sites-edit-submit'));

    await waitFor(() => {
      expect(screen.getByTestId('admin-sites-reload-list')).toHaveProperty('disabled', true);
    });
    expect(screen.getByTestId(`admin-sites-edit-${siteId}`)).toHaveProperty('disabled', true);

    resolveEdit!({ ok: true, site: { ...siteRow, name: 'Recyclerie Renommée' } });
    await waitFor(() => {
      expect(screen.getByTestId('admin-sites-reload-list')).toHaveProperty('disabled', false);
    });
  });

  it('désactive Enregistrer et n’envoie pas PATCH si le nom est vide', async () => {
    render(wrap(<AdminSitesWidget widgetId="sites" pageKey="test" />));
    await waitFor(() => expect(screen.getByText('Recyclerie Pilote')).toBeTruthy());

    fireEvent.click(screen.getByTestId(`admin-sites-edit-${siteId}`));
    const modal = await screen.findByTestId('admin-sites-edit-modal');
    fireEvent.change(within(modal).getByDisplayValue('Recyclerie Pilote'), { target: { value: '' } });

    const submit = within(modal).getByTestId('admin-sites-edit-submit');
    expect(submit).toHaveProperty('disabled', true);
    const callsBeforeClick = updateSiteMock.mock.calls.length;
    fireEvent.click(submit);
    expect(updateSiteMock.mock.calls.length).toBe(callsBeforeClick);
  });
});
