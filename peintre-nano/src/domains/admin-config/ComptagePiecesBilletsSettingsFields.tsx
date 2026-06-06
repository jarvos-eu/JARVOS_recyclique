import { Stack, Switch } from '@mantine/core';
import type { ComptagePiecesBilletsSettings } from './comptage-pieces-billets-settings';

export type ComptagePiecesBilletsSettingsFieldsProps = {
  readonly value: ComptagePiecesBilletsSettings;
  readonly onChange: (partial: Partial<ComptagePiecesBilletsSettings>) => void;
  readonly disabled?: boolean;
};

/** Champs réglages module comptage pièces/billets (clôture caisse) — admin `/admin/modules`. */
export function ComptagePiecesBilletsSettingsFields({
  value,
  onChange,
  disabled = false,
}: ComptagePiecesBilletsSettingsFieldsProps) {
  return (
    <Stack gap="md" data-testid="comptage-pieces-billets-settings-fields">
      <Switch
        label="Module activé"
        description="Ajoute l'étape comptage pièces/billets dans le wizard de clôture caisse pour ce site."
        checked={value.enabled}
        disabled={disabled}
        onChange={(e) => onChange({ enabled: e.currentTarget.checked })}
        data-testid="admin-comptage-toggle-enabled"
      />
      <Switch
        label="Autoriser le passage sans comptage"
        description="Si activé, l'opérateur peut clôturer sans saisir la grille (audit recommandé). D-CPT-07 : désactivé sur le pilote La Clique."
        checked={value.skipAllowed}
        disabled={disabled || !value.enabled}
        onChange={(e) => onChange({ skipAllowed: e.currentTarget.checked })}
        data-testid="admin-comptage-toggle-skip-allowed"
      />
      <Switch
        label="Grille complète obligatoire"
        description="Exige les 15 lignes de dénominations (quantités 0 explicites) avant clôture."
        checked={value.requireDenominationGrid}
        disabled={disabled || !value.enabled}
        onChange={(e) => onChange({ requireDenominationGrid: e.currentTarget.checked })}
        data-testid="admin-comptage-toggle-require-grid"
      />
      <Switch
        label="Afficher les pictos"
        description="Pictos stylisés dans la grille (masquables sans bloquer la saisie des quantités)."
        checked={value.showImages}
        disabled={disabled || !value.enabled}
        onChange={(e) => onChange({ showImages: e.currentTarget.checked })}
        data-testid="admin-comptage-toggle-show-images"
      />
    </Stack>
  );
}
