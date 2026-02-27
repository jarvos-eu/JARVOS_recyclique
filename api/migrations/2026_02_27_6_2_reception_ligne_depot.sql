-- Story 6.2 — Lignes de dépôt (ligne_depot)
-- Référence : references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md, schema-recyclic-dev.md
-- Colonnes : id, ticket_id FK, poids_kg, category_id FK nullable, destination, notes, is_exit, created_at, updated_at

CREATE TABLE IF NOT EXISTS ligne_depot (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id UUID NOT NULL REFERENCES ticket_depot(id) ON DELETE CASCADE,
  poids_kg NUMERIC(12,3) NOT NULL,
  category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
  destination VARCHAR(64) NOT NULL,
  notes TEXT,
  is_exit BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ligne_depot_ticket_id ON ligne_depot(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ligne_depot_category_id ON ligne_depot(category_id);
