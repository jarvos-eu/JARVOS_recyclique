/**
 * Navigation conditionnelle — Story 3.5.
 * En mode caisse verrouillé : uniquement entrées caisse + déverrouiller par PIN.
 * Sinon : toutes les entrées (RBAC géré ailleurs).
 * Story 6.1 review : lien Réception masqué si l'utilisateur n'a pas reception.access.
 */
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useCashRegisterLock } from './useCashRegisterLock';
import { CAISSE_PIN_PATH, CAISSE_SESSION_CLOSE_PATH } from './cashRegisterRoutes';

export interface NavItem {
  to: string;
  label: string;
  /** true = affiché uniquement en mode caisse (verrouillé ou non). */
  caisseOnly?: boolean;
  /** Code permission requis pour afficher le lien (ex. reception.access). Masqué si pas dans permissions. */
  permissionCode?: string;
  /** Au moins une de ces permissions suffit pour afficher le lien (ex. admin ou vie_asso.access). */
  permissionCodes?: string[];
}

const FULL_NAV_ITEMS: NavItem[] = [
  { to: '/caisse', label: 'Dashboard caisses', caisseOnly: true },
  { to: '/cash-register/session/open', label: 'Ouverture session', caisseOnly: true },
  { to: '/cash-register/sale', label: 'Saisie vente', caisseOnly: true },
  { to: CAISSE_SESSION_CLOSE_PATH, label: 'Fermeture session', caisseOnly: true },
  { to: '/admin', label: 'Admin' },
  { to: '/admin/users', label: 'Utilisateurs', permissionCode: 'admin' },
  { to: '/admin/sites', label: 'Sites', permissionCode: 'admin' },
  { to: '/admin/cash-registers', label: 'Postes caisse', permissionCode: 'admin' },
  { to: '/admin/session-manager', label: 'Sessions caisse', permissionCode: 'admin' },
  { to: '/admin/reports', label: 'Rapports caisse', permissionCode: 'admin' },
  { to: '/admin/reception', label: 'Réception admin', permissionCode: 'admin' },
  { to: '/admin/health', label: 'Santé', permissionCode: 'admin' },
  { to: '/admin/audit-log', label: 'Audit log', permissionCode: 'admin' },
  { to: '/admin/email-logs', label: 'Logs email', permissionCode: 'admin' },
  { to: '/admin/settings', label: 'Paramètres', permissionCode: 'admin' },
  { to: '/admin/db', label: 'BDD (export, purge, import)', permissionCode: 'admin' },
  { to: '/admin/import/legacy', label: 'Import legacy', permissionCode: 'admin' },
  { to: '/admin/groups', label: 'Groupes', permissionCode: 'admin' },
  { to: '/admin/permissions', label: 'Permissions', permissionCode: 'admin' },
  { to: '/reception', label: 'Réception', permissionCode: 'reception.access' },
  { to: '/profil', label: 'Profil' },
  { to: '/admin/categories', label: 'Catégories', permissionCode: 'admin' },
  { to: '/admin/quick-analysis', label: 'Analyse rapide', permissionCode: 'admin' },
  { to: '/admin/vie-associative', label: 'Vie associative', permissionCodes: ['admin', 'vie_asso.access'] },
];

/**
 * Affiche le menu caisse uniquement (dashboard, ouverture session, saisie vente,
 * déverrouiller par PIN) quand isRestricted ; sinon affiche toutes les entrées
 * (Admin, Réception, Profil, Catégories, etc.).
 */
export function AppNav() {
  const { isRestricted } = useCashRegisterLock();
  const { permissions } = useAuth();
  const location = useLocation();

  const items = isRestricted
    ? [
        ...FULL_NAV_ITEMS.filter((i) => i.caisseOnly),
        { to: CAISSE_PIN_PATH, label: 'Déverrouiller par PIN', caisseOnly: true as const },
      ]
    : FULL_NAV_ITEMS.filter((item) => {
        if (item.permissionCodes) {
          return permissions.length > 0 && item.permissionCodes.some((p) => permissions.includes(p));
        }
        return (
          !item.permissionCode ||
          (permissions.length === 0 ? true : permissions.includes(item.permissionCode))
        );
      });

  return (
    <nav aria-label="Navigation principale" data-testid="app-nav">
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {items.map((item) => (
          <li key={item.to}>
            <Link
              to={item.to}
              data-testid={`nav-${item.to.replace(/\//g, '-').replace(/^\-/, '') || 'root'}`}
              style={{
                fontWeight: location.pathname === item.to ? 'bold' : undefined,
              }}
            >
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
