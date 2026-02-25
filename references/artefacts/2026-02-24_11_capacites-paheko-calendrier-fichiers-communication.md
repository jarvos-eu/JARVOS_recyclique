# Capacites natives Paheko — Calendrier, fichiers, communication

**Date :** 2026-02-24  
**Contexte :** Session migration Paheko, idee Kanban « Calendar espace fichiers Paheko » + todo « Verifier capacites natives Paheko ».

**Sources :** paheko.cloud (sommaire aide, fonctionnalites documents, extension Agenda et contacts), recherche web.

---

## Synthese

| Domaine | Natif core | Extension | Limites / remarques |
|--------|------------|-----------|----------------------|
| **Espace fichiers / documents** | Oui | — | Centralise, dossiers, WebDAV, Collabora, partage lien + mot de passe, pieces jointes fiches membres + ecritures compta. |
| **Calendrier collaboratif (reunions, planification)** | Non | « Agenda et contacts » = agenda **individuel** par membre | Pas d'agenda collectif/partage ; pas de vue semaine/jour ; pas d'evenements recurrents. Pas d'agenda « evenements de l'association ». |
| **Activites / cotisations** | Oui | — | Inscription membres, tarifs, rappels, lien compta — pas un agenda de reunions. |
| **Communication** | Oui | — | Messagerie (mailings, messages personnels, PGP, RGPD). |

---

## Fichiers (core)

- Un seul espace documents : factures, statuts, photos, etc.
- Import fichier ou creation en ligne (texte, Office, tableur, presentation).
- Edition collaborative en ligne (Collabora Office Online).
- Acces WebDAV (compatible ownCloud/NextCloud).
- Partage par lien (mot de passe optionnel).
- Documents jointables aux fiches membres et aux ecritures comptables.

---

## Calendrier / agenda

- **Core** : pas d'agenda de reunions. « Activites et cotisations » = gestion inscriptions/cotisations + enregistrement compta, pas un calendrier partage.
- **Extension « Agenda et contacts »** :
  - Agenda **par membre** (individuel), pas d'agenda association ni partage entre membres.
  - CalDAV/CardDAV (sync mobile, Thunderbird, Vivaldi).
  - Limitations : vue mois uniquement ; pas d'evenements recurrents ; pas d'agenda collectif.

**Conclusion** : Pour un calendrier collaboratif (reunions, planification), Paheko ne fournit pas de solution native. Options : outil externe, extension future, ou conception cote Recyclic / JARVOS Nano.

---

## Communication

- Envoi de messages collectifs (mailings), personnalisation, PGP optionnel, desinscriptions, RGPD.
- Messages personnels aux membres.

---

## Impact pour JARVOS Recyclique

- **Fichiers** : s'appuyer sur Paheko pour l'espace documents assoc ; pas besoin de dupliquer en custom (sauf besoin specifique Recyclic).
- **Calendrier reunions** : ne pas attendre de solution Paheko ; traiter en idee separee (Recyclic, Nano, ou outil externe) si besoin.
- **Communication** : deja couverte en natif (mailings, messages).
