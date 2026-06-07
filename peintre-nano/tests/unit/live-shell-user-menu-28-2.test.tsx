// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { LiveShellUserMenu } from '../../src/app/shell/LiveShellUserMenu';
import { RootProviders } from '../../src/app/providers/RootProviders';

beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    configurable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }),
  });
});

afterEach(() => {
  cleanup();
});

describe('Story 28.2 — LiveShellUserMenu Mon profil', () => {
  it('affiche Mon profil entre Dashboard personnel et Déconnexion quand onProfile est fourni', async () => {
    const onProfile = vi.fn();
    const onLogout = vi.fn();
    const onPersonalDashboard = vi.fn();

    render(
      <RootProviders disableUserPrefsPersistence>
        <LiveShellUserMenu
          displayLabel="Marie Test"
          onLogout={onLogout}
          onPersonalDashboard={onPersonalDashboard}
          onProfile={onProfile}
        />
      </RootProviders>,
    );

    fireEvent.click(screen.getByTestId('live-shell-user-menu-trigger'));
    const profileItem = await waitFor(() => screen.getByTestId('live-shell-user-menu-profile'));
    expect(profileItem.textContent).toContain('Mon profil');

    const dashboardItem = screen.getByTestId('live-shell-user-menu-personal-dashboard');
    const logoutItem = screen.getByTestId('live-shell-user-menu-logout');
    const menuOrder = [dashboardItem, profileItem, logoutItem];
    for (let i = 0; i < menuOrder.length - 1; i += 1) {
      expect(menuOrder[i].compareDocumentPosition(menuOrder[i + 1]) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    }

    fireEvent.click(profileItem);
    expect(onProfile).toHaveBeenCalledTimes(1);
  });

  it('masque Mon profil si onProfile est absent', () => {
    render(
      <RootProviders disableUserPrefsPersistence>
        <LiveShellUserMenu displayLabel="Marie Test" onLogout={vi.fn()} onPersonalDashboard={vi.fn()} />
      </RootProviders>,
    );
    fireEvent.click(screen.getByTestId('live-shell-user-menu-trigger'));
    expect(screen.queryByTestId('live-shell-user-menu-profile')).toBeNull();
  });
});
