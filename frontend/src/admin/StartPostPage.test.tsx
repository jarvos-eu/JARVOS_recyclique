/**
 * Tests StartPostPage — Story 3.4.
 * Affichage sites/postes, soumission caisse, réception, messages succès/erreur.
 */
import React from 'react';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { StartPostPage } from './StartPostPage';
import * as adminApi from '../api/admin';

vi.mock('../api/admin', () => ({
  getSites: vi.fn(),
  getCashRegisters: vi.fn(),
  startCashRegister: vi.fn(),
  openPosteReception: vi.fn(),
}));

const mockToken = 'fake-admin-token';

describe('StartPostPage', () => {
  beforeEach(() => {
    vi.mocked(adminApi.getSites).mockResolvedValue([
      { id: 'site-1', name: 'Site A', is_active: true, created_at: '', updated_at: '' },
    ]);
    vi.mocked(adminApi.getCashRegisters).mockResolvedValue([
      {
        id: 'reg-1',
        site_id: 'site-1',
        name: 'Caisse 1',
        location: null,
        is_active: true,
        started_at: null,
        started_by_user_id: null,
        created_at: '',
        updated_at: '',
      },
    ]);
    vi.mocked(adminApi.startCashRegister).mockResolvedValue({} as adminApi.CashRegister);
    vi.mocked(adminApi.openPosteReception).mockResolvedValue({
      id: 'poste-1',
      opened_by_user_id: null,
      opened_at: new Date().toISOString(),
      status: 'open',
    });
  });

  it('affiche le choix Caisse / Réception au chargement', () => {
    render(<StartPostPage accessToken={mockToken} />);
    expect(screen.getByTestId('start-post-page')).toBeInTheDocument();
    expect(screen.getByTestId('start-post-choose-caisse')).toBeInTheDocument();
    expect(screen.getByTestId('start-post-choose-reception')).toBeInTheDocument();
  });

  it('au clic sur Caisse, charge les sites et affiche le formulaire caisse', async () => {
    render(<StartPostPage accessToken={mockToken} />);
    await userEvent.click(screen.getByTestId('start-post-choose-caisse'));
    await waitFor(() => {
      expect(adminApi.getSites).toHaveBeenCalledWith(mockToken);
    });
    await waitFor(() => {
      expect(screen.getByTestId('start-post-site-select')).toBeInTheDocument();
    });
    expect(within(screen.getByTestId('start-post-site-select')).getByText('Site A')).toBeInTheDocument();
  });

  it('soumission caisse appelle startCashRegister et affiche un message de succès', async () => {
    render(<StartPostPage accessToken={mockToken} />);
    await userEvent.click(screen.getByTestId('start-post-choose-caisse'));
    await waitFor(() => {
      expect(screen.getByTestId('start-post-register-select')).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(within(screen.getByTestId('start-post-register-select')).getByText(/Caisse 1/)).toBeInTheDocument();
    });
    const submitBtn = screen.getByTestId('start-post-caisse-submit');
    await waitFor(() => {
      expect(submitBtn).not.toBeDisabled();
    });
    await userEvent.click(submitBtn);
    await waitFor(() => {
      expect(adminApi.startCashRegister).toHaveBeenCalledWith(mockToken, 'site-1', 'reg-1');
    });
    const messageEl = await screen.findByTestId('start-post-message', {}, { timeout: 2000 });
    expect(messageEl).toHaveAttribute('data-message-type', 'success');
    expect(screen.getByText(/Poste caisse démarré avec succès/)).toBeInTheDocument();
  });

  it('affiche un message d’erreur en cas d’échec démarrage caisse', async () => {
    vi.mocked(adminApi.startCashRegister).mockRejectedValue(new Error('Register does not belong to site'));
    render(<StartPostPage accessToken={mockToken} />);
    await userEvent.click(screen.getByTestId('start-post-choose-caisse'));
    await waitFor(() => {
      expect(screen.getByTestId('start-post-caisse-submit')).toBeInTheDocument();
    });
    await userEvent.click(screen.getByTestId('start-post-caisse-submit'));
    await waitFor(() => {
      expect(screen.getByTestId('start-post-message')).toHaveAttribute(
        'data-message-type',
        'error'
      );
    });
    expect(screen.getByText(/Register does not belong to site/)).toBeInTheDocument();
  });

  it('au clic sur Réception, affiche le formulaire réception', async () => {
    render(<StartPostPage accessToken={mockToken} />);
    await userEvent.click(screen.getByTestId('start-post-choose-reception'));
    expect(screen.getByTestId('start-post-reception-form')).toBeInTheDocument();
    expect(screen.getByTestId('start-post-reception-submit')).toBeInTheDocument();
  });

  it('soumission réception appelle openPosteReception et affiche un message de succès', async () => {
    render(<StartPostPage accessToken={mockToken} />);
    await userEvent.click(screen.getByTestId('start-post-choose-reception'));
    await userEvent.click(screen.getByTestId('start-post-reception-submit'));
    await waitFor(() => {
      expect(adminApi.openPosteReception).toHaveBeenCalledWith(mockToken);
    });
    expect(screen.getByTestId('start-post-message')).toHaveAttribute(
      'data-message-type',
      'success'
    );
    expect(screen.getByText(/Poste réception ouvert avec succès/)).toBeInTheDocument();
  });

  it('bouton Retour réinitialise le choix de type', async () => {
    render(<StartPostPage accessToken={mockToken} />);
    await userEvent.click(screen.getByTestId('start-post-choose-caisse'));
    await waitFor(() => {
      expect(screen.getByTestId('start-post-back')).toBeInTheDocument();
    });
    await userEvent.click(screen.getByTestId('start-post-back'));
    expect(screen.getByTestId('start-post-type-choice')).toBeInTheDocument();
    expect(screen.getByTestId('start-post-choose-caisse')).toBeInTheDocument();
  });
});
