/**
 * Page saisie vente (étape sale) — Story 5.2, 5.4 (hors ligne + sync).
 * GET /v1/cash-sessions/current, GET /v1/presets/active, GET /v1/categories/sale-tickets.
 * Panier (lignes), paiements multiples, note, option sale_date. POST /v1/sales → vidage panier.
 * Hors ligne : buffer IndexedDB ; au retour en ligne envoi vers API (meme contrat 5.2).
 */
import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getCurrentCashSession,
  getPresetsActive,
  getCategoriesSaleTickets,
  postSale,
  updateCashSessionStep,
} from '../api/caisse';
import type {
  CashSessionItem,
  PresetItem,
  CategoryItem,
  SaleItemPayload,
  PaymentPayload,
} from '../api/caisse';
import { useAuth } from '../auth/AuthContext';
import { useOnlineStatus } from './useOnlineStatus';
import {
  addTicket,
  syncOfflineQueue,
  getPendingCount,
} from './offlineQueue';

export interface CartLine {
  id: string;
  category_id: string | null;
  preset_id: string | null;
  preset_name?: string;
  category_name?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  weight: number | null;
}

export function CashRegisterSalePage() {
  const { accessToken } = useAuth();
  const navigate = useNavigate();
  const online = useOnlineStatus();
  const [session, setSession] = useState<CashSessionItem | null>(null);
  const [presets, setPresets] = useState<PresetItem[]>([]);
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cart, setCart] = useState<CartLine[]>([]);
  const [payments, setPayments] = useState<PaymentPayload[]>([]);
  const [paymentMethod, setPaymentMethod] = useState('especes');
  const [paymentAmountEur, setPaymentAmountEur] = useState('');
  const [note, setNote] = useState('');
  const [saleDate, setSaleDate] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [pendingOfflineCount, setPendingOfflineCount] = useState(0);
  const [syncing, setSyncing] = useState(false);

  const loadData = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    try {
      const [current, presetsList, categoriesList] = await Promise.all([
        getCurrentCashSession(accessToken),
        getPresetsActive(accessToken),
        getCategoriesSaleTickets(accessToken),
      ]);
      setSession(current);
      setPresets(presetsList);
      setCategories(categoriesList);
      if (current && current.current_step !== 'sale') {
        await updateCashSessionStep(accessToken, current.id, 'sale');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erreur chargement');
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Story 5.4 : au retour en ligne, synchroniser la file offline.
  useEffect(() => {
    if (!online || !accessToken) return;
    let cancelled = false;
    setSyncing(true);
    syncOfflineQueue(accessToken)
      .then(() => {
        if (!cancelled) return getPendingCount();
      })
      .then((count) => {
        if (!cancelled) setPendingOfflineCount(count);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setSyncing(false);
      });
    return () => {
      cancelled = true;
    };
  }, [online, accessToken]);

  // Rafraichir le nombre de tickets en attente (apres ajout en buffer ou au mount).
  const refreshPendingCount = useCallback(async () => {
    const count = await getPendingCount();
    setPendingOfflineCount(count);
  }, []);

  useEffect(() => {
    refreshPendingCount();
  }, [refreshPendingCount]);

  const addPresetToCart = useCallback(
    (preset: PresetItem) => {
      setCart((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          category_id: preset.category_id,
          preset_id: preset.id,
          preset_name: preset.name,
          category_name: undefined,
          quantity: 1,
          unit_price: preset.preset_price,
          total_price: preset.preset_price,
          weight: null,
        },
      ]);
    },
    []
  );

  const addCategoryToCart = useCallback(
    (category: CategoryItem, quantity: number, unitPriceCents: number, weight: number | null = null) => {
      const total = quantity * unitPriceCents;
      setCart((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          category_id: category.id,
          preset_id: null,
          category_name: category.name,
          preset_name: undefined,
          quantity,
          unit_price: unitPriceCents,
          total_price: total,
          weight,
        },
      ]);
    },
    []
  );

  const removeCartLine = useCallback((id: string) => {
    setCart((prev) => prev.filter((l) => l.id !== id));
  }, []);

  const cartTotal = cart.reduce((s, l) => s + l.total_price, 0);
  const paymentsTotal = payments.reduce((s, p) => s + p.amount, 0);

  const addPayment = useCallback(() => {
    const amount = Math.round(parseFloat(paymentAmountEur || '0') * 100);
    if (amount <= 0 || Number.isNaN(amount)) return;
    setPayments((prev) => [...prev, { payment_method: paymentMethod, amount }]);
    setPaymentAmountEur('');
  }, [paymentMethod, paymentAmountEur]);

  const removePayment = useCallback((index: number) => {
    setPayments((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!session) return;
      if (cart.length === 0) {
        setError('Panier vide');
        return;
      }
      if (paymentsTotal !== cartTotal) {
        setError('La somme des paiements doit être égale au total du panier');
        return;
      }
      if (payments.length === 0) {
        setError('Ajoutez au moins un paiement');
        return;
      }
      setSubmitting(true);
      setError(null);
      const items: SaleItemPayload[] = cart.map((l) => ({
        category_id: l.category_id ?? undefined,
        preset_id: l.preset_id ?? undefined,
        quantity: l.quantity,
        unit_price: l.unit_price,
        total_price: l.total_price,
        weight: l.weight ?? undefined,
      }));
      const payload = {
        cash_session_id: session.id,
        items,
        payments,
        note: note || undefined,
        sale_date: saleDate ? `${saleDate}T00:00:00.000Z` : undefined,
      };

      try {
        if (!online) {
          // Story 5.4 : hors ligne → buffer local (IndexedDB).
          const offlineId = crypto.randomUUID();
          await addTicket({
            ...payload,
            offline_id: offlineId,
            created_at: new Date().toISOString(),
          });
          setCart([]);
          setPayments([]);
          setNote('');
          setSaleDate('');
          await refreshPendingCount();
          setSubmitting(false);
          return;
        }
        if (!accessToken) return;
        await postSale(accessToken, payload);
        setCart([]);
        setPayments([]);
        setNote('');
        setSaleDate('');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erreur enregistrement');
      } finally {
        setSubmitting(false);
      }
    },
    [
      session,
      cart,
      payments,
      paymentsTotal,
      cartTotal,
      note,
      saleDate,
      online,
      accessToken,
      refreshPendingCount,
    ]
  );

  if (loading) {
    return (
      <div data-testid="page-sale">
        <p>Chargement…</p>
      </div>
    );
  }

  if (!session) {
    return (
      <div data-testid="page-sale">
        <p>Aucune session en cours.</p>
        <button type="button" onClick={() => navigate('/caisse')}>
          Retour dashboard
        </button>
      </div>
    );
  }

  return (
    <div data-testid="page-sale">
      {/* Story 5.4 : indication hors ligne / synchronisation en attente */}
      {!online && (
        <div role="status" aria-live="polite" data-testid="offline-banner" style={{ padding: '0.5rem', background: '#f0ad4e', color: '#000', marginBottom: '0.5rem' }}>
          Hors ligne — Les ventes sont enregistrées localement et seront envoyées au retour en ligne.
        </div>
      )}
      {online && (pendingOfflineCount > 0 || syncing) && (
        <div role="status" aria-live="polite" data-testid="sync-pending-banner" style={{ padding: '0.5rem', background: '#5bc0de', color: '#000', marginBottom: '0.5rem' }}>
          {syncing
            ? `Synchronisation en cours… (${pendingOfflineCount} ticket(s) en attente)`
            : `Synchronisation en attente : ${pendingOfflineCount} ticket(s) à envoyer.`}
        </div>
      )}
      <h1>Saisie vente</h1>
      <p>Session : {session.id.slice(0, 8)}… — Fond de caisse : {(session.initial_amount / 100).toFixed(2)} €</p>

      <section aria-label="Presets">
        <h2>Boutons rapides</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {presets.map((p) => (
            <button
              key={p.id}
              type="button"
              data-testid={`preset-${p.id}`}
              onClick={() => addPresetToCart(p)}
            >
              {p.name} ({(p.preset_price / 100).toFixed(2)} €)
            </button>
          ))}
        </div>
      </section>

      <section aria-label="Panier">
        <h2>Panier</h2>
        {cart.length === 0 ? (
          <p data-testid="cart-empty">Panier vide</p>
        ) : (
          <ul data-testid="cart-lines">
            {cart.map((l) => (
              <li key={l.id}>
                {l.preset_name ?? l.category_name} × {l.quantity} = {(l.total_price / 100).toFixed(2)} €
                {l.weight != null && ` — ${l.weight} kg`}
                <button
                  type="button"
                  data-testid={`remove-line-${l.id}`}
                  onClick={() => removeCartLine(l.id)}
                >
                  Retirer
                </button>
              </li>
            ))}
          </ul>
        )}
        <p data-testid="cart-total">
          <strong>Total : {(cartTotal / 100).toFixed(2)} €</strong>
        </p>
      </section>

      <section aria-label="Catégories">
        <h2>Ajouter une ligne (catégorie)</h2>
        <select
          data-testid="category-select"
          onChange={(e) => {
            const id = e.target.value;
            if (!id) return;
            const cat = categories.find((c) => c.id === id);
            if (cat) {
              const qty = parseInt((document.getElementById('cat-quantity') as HTMLInputElement)?.value || '1', 10);
              const priceEur = (document.getElementById('cat-price') as HTMLInputElement)?.value || '0';
              const priceCents = Math.round(parseFloat(priceEur) * 100);
              const weightInput = document.getElementById('cat-weight') as HTMLInputElement;
              const weight = weightInput?.value ? parseFloat(weightInput.value) : null;
              addCategoryToCart(cat, qty, priceCents, weight);
              e.target.value = '';
            }
          }}
        >
          <option value="">— Choisir catégorie —</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <label>
          Quantité <input id="cat-quantity" type="number" min={1} defaultValue={1} data-testid="cat-quantity" />
        </label>
        <label>
          Prix unitaire (€) <input id="cat-price" type="number" step="0.01" min={0} defaultValue="0" data-testid="cat-price" />
        </label>
        <label>
          Poids (kg) <input id="cat-weight" type="number" step="0.001" min={0} data-testid="cat-weight" placeholder="Optionnel" />
        </label>
      </section>

      <section aria-label="Paiements">
        <h2>Paiements</h2>
        <div>
          <label>
            Moyen{' '}
            <select
              data-testid="payment-method"
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value)}
            >
              <option value="especes">Espèces</option>
              <option value="cheque">Chèque</option>
              <option value="cb">Carte bancaire</option>
            </select>
          </label>
          <label>
            Montant (€){' '}
            <input
              type="number"
              step="0.01"
              min={0}
              data-testid="payment-amount"
              value={paymentAmountEur}
              onChange={(e) => setPaymentAmountEur(e.target.value)}
            />
          </label>
          <button type="button" data-testid="add-payment" onClick={addPayment}>
            Ajouter
          </button>
        </div>
        <ul data-testid="payments-list">
          {payments.map((p, i) => (
            <li key={i}>
              {p.payment_method} : {(p.amount / 100).toFixed(2)} €
              <button type="button" data-testid={`remove-payment-${i}`} onClick={() => removePayment(i)}>
                Retirer
              </button>
            </li>
          ))}
        </ul>
        <p>Total paiements : {(paymentsTotal / 100).toFixed(2)} €</p>
      </section>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="sale-note">Note ticket</label>
          <input
            id="sale-note"
            type="text"
            data-testid="sale-note"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="sale-date">Date réelle (optionnel, YYYY-MM-DD)</label>
          <input
            id="sale-date"
            type="date"
            data-testid="sale-date"
            value={saleDate}
            onChange={(e) => setSaleDate(e.target.value)}
          />
        </div>
        {error && <p data-testid="sale-error">{error}</p>}
        <button
          type="submit"
          disabled={submitting || cart.length === 0 || paymentsTotal !== cartTotal}
          data-testid="sale-submit"
        >
          {submitting ? 'Enregistrement…' : 'Enregistrer le ticket'}
        </button>
      </form>

      <p>
        <button type="button" onClick={() => navigate('/cash-register/session/close')}>
          Fermer la session
        </button>
      </p>
    </div>
  );
}
