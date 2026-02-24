# Module correspondance Paheko

---

## 2026-02-24 — Mary (session max Paheko)

Module middleware dans le back-end Recyclic qui traduit les objets metier Recyclic vers les appels API Paheko. Rôle : traducteur (Recyclic domain -> API Paheko), pas synchroniseur BDD.

**Perimetre** : sessions caisse, ventes, eventuellement depots/poids (selon extension Saisie au poids). Tableaux de correspondance (ex. categories Recyclic -> categories/comptes Paheko) a definir ; matiere concrete = dumps BDD production Recyclic + Paheko quand disponibles.

**Dependances** : recherche API Paheko caisse ; recherche extension Saisie au poids ; decision source de verite caisse (artefact 08).

**Questions ouvertes** : resilience si Paheko down ; granularite des appels (par session, par ticket) ; emplacement dans l'architecture (module ModuleBase dedie, voir artefact 07).

Intention : a-conceptualiser
