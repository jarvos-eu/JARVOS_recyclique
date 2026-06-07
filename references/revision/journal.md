# Journal — ajouts révisions terrain

Une ligne par item créé ou fusion important. Le détail reste dans `domaines/<domaine>.md`.

| Date | Auteur | ID | Résumé |
|------|--------|-----|--------|
| 2026-06-07 | Strophe + agent | REV-CAISSE-01…13 | Première passe live caisse — migration depuis artefact initial ; création dossier `references/revision/` |
| 2026-06-07 | Agent DS story 28.2 | REV-TRANSVERSE-01 · REV-ADMIN-01 · REV-RECEPTION-02 | Menu Mon profil + route `/profil` + widget PIN self-service + CTA Retour au menu réception hub inactif — Investigé/Corrigé (HITL Strophe) |
| 2026-06-07 | Strophe (revue live) | REV-TRANSVERSE-01 | Menu bandeau vert : manque « Mon profil » vs legacy (`Header.jsx` → `/profil`, PIN) ; gap manifest déjà noté doc Peintre |
| 2026-06-07 | Strophe (revue live) | REV-ADMIN-01 | Gestion utilisateurs : réinit PIN efface sans création ; modal coords sans PIN ; chaîne legacy = `/profil` absente en v2 |
| 2026-06-07 | Strophe (revue live) | REV-RECEPTION-01…06 | Réception : hub vide vs liste legacy, PWA coincée, layout non resize, badges clavier, clôture ticket confuse ; saisie poids OK |
| 2026-06-07 | Strophe (revue live) | REV-TRANSVERSE-02, 03 | PWA : barre titre bleue `#228be6` vs fond ; souhait plier/déplier titre ; blocage sortie réception = REV-RECEPTION-02 |
| 2026-06-07 | Strophe (revue live) | REV-TRANSVERSE-04, 05 ; REV-ADMIN-02, 03 | UUID partout ; pavés dev admin modules ; erreur save module-config persiste après F5 ; accordéons KPI/comptage OK |
| 2026-06-07 | Strophe (revue live) | REV-ADMIN-04 | Dashboard admin : déplacer Activité & Logs vers super-admin ; pavé super-admin repliable par défaut |
| 2026-06-07 | Strophe (revue live) | REV-ADMIN-05 | Santé et signaux : langage planché, infobulles, clarifier qui fait les reco (maintenance BDD, audit sécurité) |
| 2026-06-07 | Strophe (revue live) | REV-ADMIN-06…10 | Sites & caisses : hub, édition manquante (parité legacy), retour hub, actualiser, archiver vs supprimer, vision zones |
| 2026-06-07 | Agent (import audit, collage autre session) | REV-CAISSE-14…22 | Rapport parité plancher : CLAV clavier, hub/ouverture/clôture, Paheko UI — écarts code non vus en live |
| 2026-06-07 | Agent (import audit, collage autre session) | REV-CAISSE-23 | Réf. checklist clavier § E — **pas** une demande Strophe ; contexte C2b/tags = autre chat |
| 2026-06-07 | Agent (import audit) | REV-RECEPTION-07, 08 | Dashboard terrain `/reception/dashboard` ; saisie différée réception absente Peintre |
| 2026-06-07 | Agent (révision registre) | — | Clarification index : séparation live Strophe vs import audit ; compteur P0 caisse corrigé (5) |
| 2026-06-07 | Agent (story 28.1 QA2 it.1) | REV-CAISSE-01,02,05,06,10,12 | Investigé+Corrigé (pas HITL) : session/reprise, clôture `resetCashflowDraft`, finalisation/held, virtuel hub ; compteur P0 caisse → 0 |
| 2026-06-07 | Agent (story 28.3 QA2 it.2) | REV-RECEPTION-01,03,05,06 | Doc registre : slot CREOS `history`, hub historique paginé, layout cockpit resize, clôture ticket, hint sortie stock ; correctif pagination retour hub |
| 2026-06-07 | Agent (story 28.4 QA2 it.1) | REV-ADMIN-02,03,05 · REV-TRANSVERSE-04,05 | Investigé+Corrigé (pas HITL) : copie modules/santé planché, save module-config sans ETag HTTP, badges reco responsable ; correctifs QA2 it.1 |
