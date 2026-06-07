import { describe, expect, it } from 'vitest';
import { mapUsersMePinApiDetailToFrench } from '../../src/api/users-me-client';

describe('Story 28.2 — mapUsersMePinApiDetailToFrench', () => {
  const cases = [
    {
      label: 'current password required',
      detail: 'Current password is required to change an existing PIN',
      httpStatus: 400,
      expected: 'Le mot de passe du compte est requis pour modifier un PIN existant.',
    },
    {
      label: 'current password incorrect',
      detail: 'Current password is incorrect',
      httpStatus: 400,
      expected: 'Le mot de passe du compte est incorrect.',
    },
    {
      label: '401 session expirée',
      detail: 'Not authenticated',
      httpStatus: 401,
      expected: 'Session expirée — reconnectez-vous.',
    },
    {
      label: '403 forbidden',
      detail: 'Forbidden',
      httpStatus: 403,
      expected: "Vous n'avez pas l'autorisation de modifier ce PIN.",
    },
    {
      label: 'fallback detail brut',
      detail: 'Unexpected server error',
      httpStatus: 500,
      expected: 'Unexpected server error',
    },
    {
      label: 'fallback vide',
      detail: '',
      httpStatus: 500,
      expected: 'Impossible de mettre à jour le PIN.',
    },
    {
      label: 'PIN 4 digits',
      detail: 'PIN must be exactly 4 digits',
      httpStatus: 400,
      expected: 'Le code PIN doit comporter exactement 4 chiffres.',
    },
    {
      label: 'exactly 4 digits sans préfixe PIN must',
      detail: 'exactly 4 digits',
      httpStatus: 400,
      expected: 'Le code PIN doit comporter exactement 4 chiffres.',
    },
  ] as const;

  it.each(cases)('$label', ({ detail, httpStatus, expected }) => {
    expect(mapUsersMePinApiDetailToFrench(detail, httpStatus)).toBe(expected);
  });
});
