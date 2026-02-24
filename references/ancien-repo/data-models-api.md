# Modèles de données — RecyClique 1.4.4 (part: api)

**ORM :** SQLAlchemy. **Migrations :** Alembic. **BDD :** PostgreSQL.

---

## Entités (référence migration)

| Modèle | Rôle |
|--------|------|
| **User** | Utilisateur (rôles UserRole, statuts UserStatus) |
| **UserSession** | Session utilisateur |
| **UserStatusHistory** | Historique statuts utilisateur |
| **LoginHistory** | Historique connexions |
| **RegistrationRequest** | Demandes d’inscription |
| **Site** | Site / ressourcerie |
| **Deposit** | Dépôt (lié bot / réception) |
| **Sale**, **SaleItem** | Vente et lignes de vente |
| **PaymentTransaction** | Transaction de paiement |
| **CashSession**, **CashSessionStep** | Session de caisse et étapes |
| **CashRegister** | Poste de caisse |
| **PosteReception**, **TicketDepot**, **LigneDepot** | Réception (postes, tickets, lignes de dépôt) ; LigneDepot.Destination |
| **Category** | Catégories EEE (arborescence) |
| **PresetButton**, **ButtonType** | Boutons presets caisse |
| **Setting** | Paramètres applicatifs |
| **Permission**, **Group** | Permissions et groupes (tables association user_groups, group_permissions) |
| **AdminSetting** | Réglages admin |
| **AuditLog**, **AuditActionType** | Journal d’audit |
| **EmailLog**, **EmailStatus**, **EmailType** | Logs et statuts email (Brevo) |
| **EmailEvent**, **EmailEventType** | Événements webhook Brevo (table `email_events`, utilisé par email_webhook_service) |
| **SyncLog** | Logs de synchronisation (ex. kDrive) |
| **LegacyCategoryMappingCache** | Cache de mapping catégories legacy |

---

## Relations (à confirmer dans le schéma Alembic)

- User ↔ Site, UserSession, LoginHistory, RegistrationRequest, Group (M2M), Deposit, Sales, CashSession…
- CashSession ↔ CashRegister, Sale, User…
- TicketDepot ↔ LigneDepot, PosteReception…
- Category (auto-référence / hiérarchie), PresetButton (catégorie, type bouton).

Pour la migration v0.1.0 : reprendre le schéma Alembic actuel (`api/alembic/`) et les modèles dans `api/src/recyclic_api/models/` pour décider ce qui est conservé, fusionné ou supprimé dans le nouveau backend.
