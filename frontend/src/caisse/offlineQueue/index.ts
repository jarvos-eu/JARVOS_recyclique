/**
 * File offline caisse — Story 5.4.
 * Buffer local (IndexedDB) + envoi au retour en ligne (meme contrat que 5.2).
 */
export type { BufferedTicket } from './types';
export { addTicket, getAllTickets, removeTicket, getPendingCount } from './indexedDb';
export { syncOfflineQueue } from './sync';
export type { SyncResult } from './sync';
