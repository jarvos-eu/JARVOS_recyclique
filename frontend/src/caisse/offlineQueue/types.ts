/**
 * Types file offline — Story 5.4.
 * Meme structure que payload POST /v1/sales + offline_id et created_at locaux.
 */
import type { SaleCreatePayload } from '../../api/caisse';

export interface BufferedTicket extends SaleCreatePayload {
  /** Id client pour idempotence cote API (dedup au rejeu). */
  offline_id: string;
  /** Date/heure de mise en buffer (ISO). */
  created_at: string;
}
