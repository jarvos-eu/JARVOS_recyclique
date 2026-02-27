/**
 * Ecran admin « Démarrer un poste » (caisse ou réception) — Story 3.4.
 * Route suggérée : /admin/start-post.
 * Choix Caisse (sites → postes → Démarrer) ou Réception (Ouvrir un poste).
 */
import React, { useCallback, useEffect, useState } from 'react';
import {
  getSites,
  getCashRegisters,
  startCashRegister,
  openPosteReception,
} from '../api/admin';
import type { Site, CashRegister } from '../api/admin';

export interface StartPostPageProps {
  /** Token JWT (admin). */
  accessToken: string;
  /** Optionnel : callback après succès (ex. navigation). */
  onSuccess?: () => void;
}

type PostType = 'caisse' | 'reception';

export function StartPostPage({ accessToken, onSuccess }: StartPostPageProps) {
  const [postType, setPostType] = useState<PostType | null>(null);
  const [sites, setSites] = useState<Site[]>([]);
  const [registers, setRegisters] = useState<CashRegister[]>([]);
  const [selectedSiteId, setSelectedSiteId] = useState<string>('');
  const [selectedRegisterId, setSelectedRegisterId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [loadingSites, setLoadingSites] = useState(false);
  const [loadingRegisters, setLoadingRegisters] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const loadSites = useCallback(async () => {
    if (!accessToken) return;
    setLoadingSites(true);
    setMessage(null);
    try {
      const list = await getSites(accessToken);
      setSites(list);
      if (list.length > 0 && !selectedSiteId) setSelectedSiteId(list[0].id);
    } catch (e) {
      setMessage({
        type: 'error',
        text: e instanceof Error ? e.message : 'Erreur chargement sites',
      });
    } finally {
      setLoadingSites(false);
    }
  }, [accessToken, selectedSiteId]);

  const loadRegisters = useCallback(async () => {
    if (!accessToken || !selectedSiteId) {
      setRegisters([]);
      return;
    }
    setLoadingRegisters(true);
    try {
      const list = await getCashRegisters(accessToken, selectedSiteId);
      setRegisters(list);
      setSelectedRegisterId(list.length > 0 ? list[0].id : '');
    } catch (e) {
      setMessage({
        type: 'error',
        text: e instanceof Error ? e.message : 'Erreur chargement postes',
      });
      setRegisters([]);
    } finally {
      setLoadingRegisters(false);
    }
  }, [accessToken, selectedSiteId]);

  useEffect(() => {
    if (postType === 'caisse') loadSites();
  }, [postType, loadSites]);

  useEffect(() => {
    if (postType === 'caisse' && selectedSiteId) loadRegisters();
    else setRegisters([]);
  }, [postType, selectedSiteId, loadRegisters]);

  const handleStartCaisse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSiteId || !selectedRegisterId) return;
    setLoading(true);
    setMessage(null);
    try {
      await startCashRegister(accessToken, selectedSiteId, selectedRegisterId);
      setMessage({ type: 'success', text: 'Poste caisse démarré avec succès.' });
      onSuccess?.();
      loadRegisters();
    } catch (e) {
      setMessage({
        type: 'error',
        text: e instanceof Error ? e.message : 'Erreur démarrage poste caisse',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleOpenReception = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      await openPosteReception(accessToken);
      setMessage({ type: 'success', text: 'Poste réception ouvert avec succès.' });
      onSuccess?.();
    } catch (e) {
      setMessage({
        type: 'error',
        text: e instanceof Error ? e.message : 'Erreur ouverture poste réception',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div data-testid="start-post-page" role="region" aria-label="Démarrer un poste">
      <h1>Démarrer un poste</h1>
      {!postType ? (
        <div data-testid="start-post-type-choice">
          <p>Choisir le type de poste :</p>
          <button
            type="button"
            data-testid="start-post-choose-caisse"
            onClick={() => setPostType('caisse')}
          >
            Caisse
          </button>
          <button
            type="button"
            data-testid="start-post-choose-reception"
            onClick={() => setPostType('reception')}
          >
            Réception
          </button>
        </div>
      ) : (
        <>
          <button
            type="button"
            data-testid="start-post-back"
            onClick={() => {
              setPostType(null);
              setMessage(null);
            }}
          >
            Retour
          </button>
          {message && (
            <div
              role="alert"
              data-testid="start-post-message"
              data-message-type={message.type}
            >
              {message.text}
            </div>
          )}
          {postType === 'caisse' && (
            <form onSubmit={handleStartCaisse} data-testid="start-post-caisse-form">
              <h2>Démarrer un poste caisse</h2>
              {loadingSites ? (
                <p data-testid="start-post-loading-sites">Chargement des sites…</p>
              ) : (
                <>
                  <label htmlFor="start-post-site">Site</label>
                  <select
                    id="start-post-site"
                    data-testid="start-post-site-select"
                    value={selectedSiteId}
                    onChange={(e) => setSelectedSiteId(e.target.value)}
                  >
                    <option value="">— Choisir —</option>
                    {sites.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                  {selectedSiteId && (
                    <>
                      {loadingRegisters ? (
                        <p data-testid="start-post-loading-registers">Chargement des postes…</p>
                      ) : (
                        <>
                          <label htmlFor="start-post-register">Poste de caisse</label>
                          <select
                            id="start-post-register"
                            data-testid="start-post-register-select"
                            value={selectedRegisterId}
                            onChange={(e) => setSelectedRegisterId(e.target.value)}
                          >
                            <option value="">— Choisir —</option>
                            {registers.map((r) => (
                              <option key={r.id} value={r.id}>
                                {r.name}
                                {r.started_at ? ' (déjà démarré)' : ''}
                              </option>
                            ))}
                          </select>
                        </>
                      )}
                    </>
                  )}
                  <button
                    type="submit"
                    data-testid="start-post-caisse-submit"
                    disabled={loading || !selectedSiteId || !selectedRegisterId || loadingRegisters}
                  >
                    {loading ? 'En cours…' : 'Démarrer ce poste'}
                  </button>
                </>
              )}
            </form>
          )}
          {postType === 'reception' && (
            <form onSubmit={handleOpenReception} data-testid="start-post-reception-form">
              <h2>Ouvrir un poste réception</h2>
              <button
                type="submit"
                data-testid="start-post-reception-submit"
                disabled={loading}
              >
                {loading ? 'En cours…' : 'Ouvrir un poste réception'}
              </button>
            </form>
          )}
        </>
      )}
    </div>
  );
}
