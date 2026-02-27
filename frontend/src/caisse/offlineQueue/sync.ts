/**
 * Synchronisation file offline → API au retour en ligne — Story 5.4.
 * Envoi ticket par ticket (meme contrat que 5.2), retry en cas d'echec (garder en buffer).
 */
import { postSale } from '../../api/caisse';
import { getAllTickets, removeTicket } from './indexedDb';

export interface SyncResult {
  sent: number;
  failed: number;
  errors: string[];
}

/**
 * Envoie tous les tickets du buffer vers POST /v1/sales (avec offline_id).
 * En cas de succes (201) : retire du buffer. En cas d'echec : laisse en buffer pour retry.
 */
export async function syncOfflineQueue(accessToken: string): Promise<SyncResult> {
  const tickets = await getAllTickets();
  const result: SyncResult = { sent: 0, failed: 0, errors: [] };

  for (const ticket of tickets) {
    try {
      const payload = {
        cash_session_id: ticket.cash_session_id,
        items: ticket.items,
        payments: ticket.payments,
        note: ticket.note ?? undefined,
        sale_date: ticket.sale_date ?? undefined,
        offline_id: ticket.offline_id,
      };
      await postSale(accessToken, payload);
      await removeTicket(ticket.offline_id);
      result.sent += 1;
    } catch (e) {
      result.failed += 1;
      result.errors.push(
        `${ticket.offline_id}: ${e instanceof Error ? e.message : String(e)}`
      );
    }
  }

  return result;
}
