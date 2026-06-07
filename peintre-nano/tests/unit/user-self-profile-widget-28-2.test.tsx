// @vitest-environment jsdom
import '@mantine/core/styles.css';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createMockAuthAdapter } from '../../src/app/auth/mock-auth-adapter';
import { createDefaultDemoEnvelope } from '../../src/app/auth/default-demo-auth-adapter';
import { RootProviders } from '../../src/app/providers/RootProviders';
import { UserSelfProfileWidget } from '../../src/domains/transverse/UserSelfProfileWidget';
import '../../src/registry';

const meProfile = {
  id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  username: 'marie@example.com',
  first_name: 'Marie',
  last_name: 'Test',
  email: 'marie@example.com',
  role: 'user',
};

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

describe('Story 28.2 — UserSelfProfileWidget PIN self-service', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'matchMedia',
      vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    );
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('affiche une alerte si fetchUsersMeProfile retourne null', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/users/me') && method === 'GET') {
        return Promise.resolve({
          ok: false,
          status: 404,
          text: async () => '',
          json: async () => null,
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '{}',
        json: async () => ({}),
      } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: meProfile.id },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <UserSelfProfileWidget widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => {
      expect(screen.getByTestId('user-profile-load-error')).toBeTruthy();
    });
    expect(screen.getByTestId('user-profile-load-error').textContent).toMatch(/Impossible de charger votre profil/i);
  });

  it('masque les champs PIN en saisie password', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/users/me') && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify(meProfile),
          json: async () => meProfile,
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '{}',
        json: async () => ({}),
      } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: meProfile.id },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <UserSelfProfileWidget widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => screen.getByTestId('user-profile-pin-section'));
    expect(screen.getByTestId('user-profile-pin-input').getAttribute('type')).toBe('password');
    expect(screen.getByTestId('user-profile-pin-confirm-input').getAttribute('type')).toBe('password');
  });

  it('enregistre un premier PIN via PUT /v1/users/me/pin', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/users/me') && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify(meProfile),
          json: async () => meProfile,
        } as Response);
      }
      if (url.includes('/v1/users/me/pin') && method === 'PUT') {
        const pinBody = JSON.stringify({ message: 'PIN successfully set' });
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => pinBody,
          json: async () => JSON.parse(pinBody),
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '{}',
        json: async () => ({}),
      } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: meProfile.id },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <UserSelfProfileWidget widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => screen.getByTestId('user-profile-pin-section'));
    fireEvent.change(screen.getByTestId('user-profile-pin-input'), { target: { value: '1234' } });
    fireEvent.change(screen.getByTestId('user-profile-pin-confirm-input'), { target: { value: '1234' } });
    fireEvent.click(screen.getByTestId('user-profile-pin-submit'));

    await waitFor(() => {
      expect(screen.getByTestId('user-profile-pin-success')).toBeTruthy();
    });
    const pinPutCall = fetchMock.mock.calls.find(([inp, init]) => {
      const url = requestUrl(inp as RequestInfo);
      const method = (init?.method ?? 'GET').toUpperCase();
      return url.includes('/v1/users/me/pin') && method === 'PUT';
    });
    expect(pinPutCall).toBeTruthy();
    expect(JSON.parse(String(pinPutCall?.[1]?.body))).toEqual({ pin: '1234' });
  });

  it('affiche une erreur si changement PIN sans mot de passe (API 400)', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/users/me') && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify(meProfile),
          json: async () => meProfile,
        } as Response);
      }
      if (url.includes('/v1/users/me/pin') && method === 'PUT') {
        const errBody = JSON.stringify({ detail: 'Current password is required to change an existing PIN' });
        return Promise.resolve({
          ok: false,
          status: 400,
          text: async () => errBody,
          json: async () => JSON.parse(errBody),
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '{}',
        json: async () => ({}),
      } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: meProfile.id },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <UserSelfProfileWidget widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => screen.getByTestId('user-profile-pin-section'));
    fireEvent.change(screen.getByTestId('user-profile-pin-input'), { target: { value: '5678' } });
    fireEvent.change(screen.getByTestId('user-profile-pin-confirm-input'), { target: { value: '5678' } });
    fireEvent.click(screen.getByTestId('user-profile-pin-submit'));

    await waitFor(() => {
      expect(screen.getByTestId('user-profile-pin-error').textContent).toMatch(/mot de passe du compte est requis/i);
    });
  });

  it('refuse un PIN client invalide (≠ 4 chiffres) sans appeler PUT', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/users/me') && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify(meProfile),
          json: async () => meProfile,
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '{}',
        json: async () => ({}),
      } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: meProfile.id },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <UserSelfProfileWidget widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => screen.getByTestId('user-profile-pin-section'));
    fireEvent.change(screen.getByTestId('user-profile-pin-input'), { target: { value: '12' } });
    fireEvent.change(screen.getByTestId('user-profile-pin-confirm-input'), { target: { value: '12' } });
    fireEvent.click(screen.getByTestId('user-profile-pin-submit'));

    await waitFor(() => {
      expect(screen.getByTestId('user-profile-pin-error').textContent).toMatch(/exactement 4 chiffres/i);
    });
    expect(
      fetchMock.mock.calls.some(([inp, init]) => {
        const url = requestUrl(inp as RequestInfo);
        return url.includes('/v1/users/me/pin') && (init?.method ?? 'GET').toUpperCase() === 'PUT';
      }),
    ).toBe(false);
  });

  it('refuse une confirmation PIN différente sans appeler PUT', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/users/me') && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify(meProfile),
          json: async () => meProfile,
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '{}',
        json: async () => ({}),
      } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: meProfile.id },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <UserSelfProfileWidget widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => screen.getByTestId('user-profile-pin-section'));
    fireEvent.change(screen.getByTestId('user-profile-pin-input'), { target: { value: '1234' } });
    fireEvent.change(screen.getByTestId('user-profile-pin-confirm-input'), { target: { value: '5678' } });
    fireEvent.click(screen.getByTestId('user-profile-pin-submit'));

    await waitFor(() => {
      expect(screen.getByTestId('user-profile-pin-error').textContent).toMatch(/ne correspondent pas/i);
    });
    expect(
      fetchMock.mock.calls.some(([inp, init]) => {
        const url = requestUrl(inp as RequestInfo);
        return url.includes('/v1/users/me/pin') && (init?.method ?? 'GET').toUpperCase() === 'PUT';
      }),
    ).toBe(false);
  });

  it('affiche une erreur si mot de passe incorrect (API 400)', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/users/me') && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify(meProfile),
          json: async () => meProfile,
        } as Response);
      }
      if (url.includes('/v1/users/me/pin') && method === 'PUT') {
        const errBody = JSON.stringify({ detail: 'Current password is incorrect' });
        return Promise.resolve({
          ok: false,
          status: 400,
          text: async () => errBody,
          json: async () => JSON.parse(errBody),
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '{}',
        json: async () => ({}),
      } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: meProfile.id },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <UserSelfProfileWidget widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => screen.getByTestId('user-profile-pin-section'));
    fireEvent.change(screen.getByTestId('user-profile-pin-input'), { target: { value: '5678' } });
    fireEvent.change(screen.getByTestId('user-profile-pin-confirm-input'), { target: { value: '5678' } });
    fireEvent.change(screen.getByTestId('user-profile-current-password-input'), { target: { value: 'wrong-pass' } });
    fireEvent.click(screen.getByTestId('user-profile-pin-submit'));

    await waitFor(() => {
      expect(screen.getByTestId('user-profile-pin-error').textContent).toMatch(/mot de passe du compte est incorrect/i);
    });
  });

  it('enregistre un changement PIN avec current_password dans le corps PUT', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = requestUrl(input);
      const method = (init?.method ?? 'GET').toUpperCase();
      if (url.includes('/v1/users/me') && method === 'GET') {
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify(meProfile),
          json: async () => meProfile,
        } as Response);
      }
      if (url.includes('/v1/users/me/pin') && method === 'PUT') {
        const pinBody = JSON.stringify({ message: 'PIN successfully set' });
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => pinBody,
          json: async () => JSON.parse(pinBody),
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '{}',
        json: async () => ({}),
      } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    const auth = createMockAuthAdapter({
      session: { authenticated: true, userId: meProfile.id },
      envelope: createDefaultDemoEnvelope(),
      accessToken: 'tok',
    });

    render(
      <RootProviders authAdapter={auth} disableUserPrefsPersistence>
        <UserSelfProfileWidget widgetProps={{}} />
      </RootProviders>,
    );

    await waitFor(() => screen.getByTestId('user-profile-pin-section'));
    fireEvent.change(screen.getByTestId('user-profile-pin-input'), { target: { value: '5678' } });
    fireEvent.change(screen.getByTestId('user-profile-pin-confirm-input'), { target: { value: '5678' } });
    fireEvent.change(screen.getByTestId('user-profile-current-password-input'), { target: { value: 'secret-pass' } });
    fireEvent.click(screen.getByTestId('user-profile-pin-submit'));

    await waitFor(() => {
      expect(screen.getByTestId('user-profile-pin-success')).toBeTruthy();
    });
    const pinPutCall = fetchMock.mock.calls.find(([inp, init]) => {
      const url = requestUrl(inp as RequestInfo);
      const method = (init?.method ?? 'GET').toUpperCase();
      return url.includes('/v1/users/me/pin') && method === 'PUT';
    });
    expect(JSON.parse(String(pinPutCall?.[1]?.body))).toEqual({
      pin: '5678',
      current_password: 'secret-pass',
    });
  });
});
