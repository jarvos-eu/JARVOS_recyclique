/**
 * Page fermeture de session de caisse — Story 5.1, 5.3.
 * GET /v1/cash-sessions/current (totaux total_sales, total_items), formulaire closing_amount,
 * actual_amount, variance_comment, POST /v1/cash-sessions/{id}/close, redirection dashboard.
 */
import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCurrentCashSession, closeCashSession } from '../api/caisse';
import type { CashSessionItem } from '../api/caisse';
import { useAuth } from '../auth/AuthContext';

export function CashRegisterSessionClosePage() {
  const { accessToken } = useAuth();
  const navigate = useNavigate();
  const [session, setSession] = useState<CashSessionItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [closingAmount, setClosingAmount] = useState('');
  const [actualAmount, setActualAmount] = useState('');
  const [varianceComment, setVarianceComment] = useState('');

  const loadCurrent = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    try {
      const current = await getCurrentCashSession(accessToken);
      setSession(current);
      if (current) {
        setClosingAmount((current.current_amount / 100).toFixed(2));
        setActualAmount((current.current_amount / 100).toFixed(2));
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur chargement');
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    loadCurrent();
  }, [loadCurrent]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!accessToken || !session) return;
      setSubmitting(true);
      setError(null);
      try {
        const closingCents = Math.round(parseFloat(closingAmount || '0') * 100);
        const actualCents = Math.round(parseFloat(actualAmount || '0') * 100);
        await closeCashSession(accessToken, session.id, {
          closing_amount: closingCents,
          actual_amount: actualCents,
          variance_comment: varianceComment || undefined,
        });
        navigate('/caisse');
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Erreur fermeture');
      } finally {
        setSubmitting(false);
      }
    },
    [accessToken, session, closingAmount, actualAmount, varianceComment, navigate]
  );

  if (loading) {
    return (
      <div data-testid="cash-register-session-close-page">
        <p>Chargement…</p>
      </div>
    );
  }

  if (!session) {
    return (
      <div data-testid="cash-register-session-close-page">
        <p>Aucune session en cours.</p>
        <button type="button" onClick={() => navigate('/caisse')}>
          Retour dashboard
        </button>
      </div>
    );
  }

  return (
    <div data-testid="cash-register-session-close-page">
      <h1>Fermeture de session</h1>
      <p>Session ouverte le {new Date(session.opened_at).toLocaleString()}</p>
      <p>Fond de caisse : {(session.initial_amount / 100).toFixed(2)} €</p>
      {(session.total_sales != null || session.total_items != null) && (
        <p data-testid="session-close-totals">
          Total ventes : {(session.total_sales ?? 0) / 100} € — Nombre de lignes : {session.total_items ?? 0}
        </p>
      )}
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="closing-amount">Montant de clôture (€)</label>
          <input
            id="closing-amount"
            type="number"
            step="0.01"
            data-testid="session-close-closing-amount"
            value={closingAmount}
            onChange={(e) => setClosingAmount(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="actual-amount">Montant compté (€)</label>
          <input
            id="actual-amount"
            type="number"
            step="0.01"
            data-testid="session-close-actual-amount"
            value={actualAmount}
            onChange={(e) => setActualAmount(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="variance-comment">Commentaire écart</label>
          <input
            id="variance-comment"
            type="text"
            data-testid="session-close-variance-comment"
            value={varianceComment}
            onChange={(e) => setVarianceComment(e.target.value)}
          />
        </div>
        {error && <p data-testid="session-close-error">{error}</p>}
        <button type="submit" disabled={submitting} data-testid="session-close-submit">
          {submitting ? 'Fermeture…' : 'Fermer la session'}
        </button>
      </form>
    </div>
  );
}
