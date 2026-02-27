/**
 * Page ouverture de session de caisse — Story 5.1.
 * GET /v1/cash-registers, pour différée GET /v1/cash-sessions/deferred/check,
 * POST /v1/cash-sessions avec initial_amount, register_id, optionnel opened_at.
 */
import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  getCashRegisters,
  getCashSessionDeferredCheck,
  openCashSession,
} from '../api/caisse';
import type { CashRegisterItem } from '../api/caisse';
import { useAuth } from '../auth/AuthContext';

export function CashRegisterSessionOpenPage() {
  const { accessToken } = useAuth();
  const [searchParams] = useSearchParams();
  const registerIdParam = searchParams.get('register_id');
  const navigate = useNavigate();
  const [registers, setRegisters] = useState<CashRegisterItem[]>([]);
  const [registerId, setRegisterId] = useState(registerIdParam ?? '');
  const [initialAmountEur, setInitialAmountEur] = useState('');
  const [sessionType, setSessionType] = useState<'real' | 'virtual' | 'deferred'>('real');
  const [deferredDate, setDeferredDate] = useState('');
  const [deferredCheckMessage, setDeferredCheckMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (registerIdParam) setRegisterId(registerIdParam);
  }, [registerIdParam]);

  const loadRegisters = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    try {
      const list = await getCashRegisters(accessToken);
      setRegisters(list);
      if (list.length > 0 && !registerId) setRegisterId(list[0].id);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur chargement');
    } finally {
      setLoading(false);
    }
  }, [accessToken, registerId]);

  useEffect(() => {
    loadRegisters();
  }, [loadRegisters]);

  const checkDeferred = useCallback(async () => {
    if (sessionType !== 'deferred' || !deferredDate || !accessToken) return;
    setDeferredCheckMessage(null);
    try {
      const result = await getCashSessionDeferredCheck(accessToken, deferredDate);
      setDeferredCheckMessage(
        result.has_session
          ? 'Une session différée existe déjà pour cette date.'
          : 'Aucune session pour cette date, vous pouvez continuer.'
      );
    } catch (e) {
      setDeferredCheckMessage(e instanceof Error ? e.message : 'Erreur vérification');
    }
  }, [sessionType, deferredDate, accessToken]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!accessToken || !registerId) return;
      const amount = Math.round(parseFloat(initialAmountEur || '0') * 100);
      if (amount < 0 || Number.isNaN(amount)) {
        setError('Montant invalide');
        return;
      }
      setSubmitting(true);
      setError(null);
      try {
        const body: {
          initial_amount: number;
          register_id: string;
          opened_at?: string;
          session_type: string;
        } = {
          initial_amount: amount,
          register_id: registerId,
          session_type: sessionType,
        };
        if (sessionType === 'deferred' && deferredDate) {
          body.opened_at = `${deferredDate}T00:00:00.000Z`;
        }
        await openCashSession(accessToken, body);
        navigate('/cash-register/sale');
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Erreur ouverture session');
      } finally {
        setSubmitting(false);
      }
    },
    [
      accessToken,
      registerId,
      initialAmountEur,
      sessionType,
      deferredDate,
      navigate,
    ]
  );

  if (loading) {
    return (
      <div data-testid="page-session-open">
        <p>Chargement…</p>
      </div>
    );
  }

  return (
    <div data-testid="page-session-open">
      <h1>Ouverture de session</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="session-type">Type</label>
          <select
            id="session-type"
            data-testid="session-open-type"
            value={sessionType}
            onChange={(e) =>
              setSessionType(e.target.value as 'real' | 'virtual' | 'deferred')
            }
          >
            <option value="real">Réelle</option>
            <option value="virtual">Virtuelle</option>
            <option value="deferred">Différée</option>
          </select>
        </div>
        <div>
          <label htmlFor="register">Poste</label>
          <select
            id="register"
            data-testid="session-open-register"
            value={registerId}
            onChange={(e) => setRegisterId(e.target.value)}
            required
          >
            <option value="">— Choisir —</option>
            {registers.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="initial-amount">Fond de caisse (€)</label>
          <input
            id="initial-amount"
            type="number"
            step="0.01"
            min="0"
            data-testid="session-open-initial-amount"
            value={initialAmountEur}
            onChange={(e) => setInitialAmountEur(e.target.value)}
            required
          />
        </div>
        {sessionType === 'deferred' && (
          <>
            <div>
              <label htmlFor="deferred-date">Date réelle (YYYY-MM-DD)</label>
              <input
                id="deferred-date"
                type="date"
                data-testid="session-open-deferred-date"
                value={deferredDate}
                onChange={(e) => setDeferredDate(e.target.value)}
              />
            </div>
            <button type="button" onClick={checkDeferred} data-testid="session-open-deferred-check">
              Vérifier doublon
            </button>
            {deferredCheckMessage && (
              <p data-testid="session-open-deferred-message">{deferredCheckMessage}</p>
            )}
          </>
        )}
        {error && <p data-testid="session-open-error">{error}</p>}
        <button type="submit" disabled={submitting} data-testid="session-open-submit">
          {submitting ? 'Ouverture…' : 'Ouvrir la session'}
        </button>
      </form>
    </div>
  );
}
