/**
 * Dashboard admin — Story 8.1, 8.2, 8.6.
 * Liens vers Utilisateurs, Sites, Postes caisse, Sessions, Rapports, Comptabilité Paheko.
 */
import React, { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Stack, Title, Anchor } from '@mantine/core';
import { useAuth } from '../auth/AuthContext';
import { getPahekoComptaUrl } from '../api/adminPahekoCompta';

export function AdminDashboardPage() {
  const { permissions, accessToken } = useAuth();
  const isAdmin = permissions.includes('admin');
  const [pahekoComptaUrl, setPahekoComptaUrl] = useState<string | null>(null);

  const loadPahekoUrl = useCallback(async () => {
    if (!isAdmin || !accessToken) return;
    try {
      const data = await getPahekoComptaUrl(accessToken);
      setPahekoComptaUrl(data.url ?? null);
    } catch {
      setPahekoComptaUrl(null);
    }
  }, [isAdmin, accessToken]);

  useEffect(() => {
    loadPahekoUrl();
  }, [loadPahekoUrl]);

  return (
    <Stack gap="md" data-testid="page-admin">
      <Title order={1}>Admin</Title>
      {isAdmin && (
        <Stack gap="xs">
          <p>
            <Anchor component={Link} to="/admin/users">
              Utilisateurs
            </Anchor>
          </p>
          <p>
            <Anchor component={Link} to="/admin/sites">
              Sites
            </Anchor>
          </p>
          <p>
            <Anchor component={Link} to="/admin/cash-registers">
              Postes de caisse
            </Anchor>
          </p>
          <p>
            <Anchor component={Link} to="/admin/session-manager">
              Gestionnaire de sessions caisse
            </Anchor>
          </p>
          <p>
            <Anchor component={Link} to="/admin/reports">
              Rapports caisse
            </Anchor>
          </p>
          <p>
            <Anchor component={Link} to="/admin/categories">
              Catégories
            </Anchor>
          </p>
          <p>
            <Anchor component={Link} to="/admin/reception">
              Réception (stats, tickets)
            </Anchor>
          </p>
          <p>
            <Anchor component={Link} to="/admin/health">
              Santé
            </Anchor>
          </p>
          <p>
            <Anchor component={Link} to="/admin/audit-log">
              Audit log
            </Anchor>
          </p>
          <p>
            <Anchor component={Link} to="/admin/email-logs">
              Logs email
            </Anchor>
          </p>
          <p>
            <Anchor component={Link} to="/admin/settings">
              Paramètres
            </Anchor>
          </p>
          <p>
            <Anchor component={Link} to="/admin/db">
              BDD (export, purge, import)
            </Anchor>
          </p>
          <p>
            <Anchor component={Link} to="/admin/import/legacy">
              Import legacy
            </Anchor>
          </p>
          {pahekoComptaUrl && (
            <p>
              <Anchor href={pahekoComptaUrl} target="_blank" rel="noopener noreferrer">
                Comptabilité (Paheko)
              </Anchor>
            </p>
          )}
        </Stack>
      )}
    </Stack>
  );
}
