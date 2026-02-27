-- Story 6.1 — Réception postes et tickets de dépôt
-- Tables : poste_reception (alignement 1.4.4 + created_at/updated_at), ticket_depot.
-- Référence : references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md

-- poste_reception : si la table existe déjà (Story 3.4), ajouter les colonnes manquantes et index
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'poste_reception') THEN
    ALTER TABLE poste_reception ADD COLUMN IF NOT EXISTS closed_at TIMESTAMPTZ;
    ALTER TABLE poste_reception ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now();
    ALTER TABLE poste_reception ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();
    ALTER TABLE poste_reception ALTER COLUMN status SET DEFAULT 'opened';
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_poste_reception_opened_by_user_id') THEN
      CREATE INDEX idx_poste_reception_opened_by_user_id ON poste_reception(opened_by_user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_poste_reception_status') THEN
      CREATE INDEX idx_poste_reception_status ON poste_reception(status);
    END IF;
  ELSE
    CREATE TABLE poste_reception (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      opened_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
      opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      closed_at TIMESTAMPTZ,
      status VARCHAR(32) NOT NULL DEFAULT 'opened',
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX idx_poste_reception_opened_by_user_id ON poste_reception(opened_by_user_id);
    CREATE INDEX idx_poste_reception_status ON poste_reception(status);
  END IF;
END $$;

-- ticket_depot
CREATE TABLE IF NOT EXISTS ticket_depot (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  poste_id UUID NOT NULL REFERENCES poste_reception(id) ON DELETE CASCADE,
  benevole_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  closed_at TIMESTAMPTZ,
  status VARCHAR(32) NOT NULL DEFAULT 'opened',
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ticket_depot_poste_id ON ticket_depot(poste_id);
CREATE INDEX IF NOT EXISTS idx_ticket_depot_benevole_user_id ON ticket_depot(benevole_user_id);
