/**
 * Persistance identité poste partagé — IndexedDB uniquement (Epic 27.4).
 * Interdit localStorage / sessionStorage pour device_id ou secret autoritaires.
 */

export type DeviceIdentityRecord = {
  readonly device_id: string;
  readonly device_secret: string;
  readonly enrolled_at: string;
};

const DB_NAME = 'recyclique-device-identity';
const DB_VERSION = 1;
const STORE_NAME = 'credentials';
const RECORD_KEY = 'current';
const HINT_KEY = 'enrollment-hint';

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    if (typeof indexedDB === 'undefined') {
      reject(new Error('IndexedDB indisponible'));
      return;
    }
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME);
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error ?? new Error('IndexedDB open failed'));
  });
}

async function withStore<T>(
  mode: IDBTransactionMode,
  fn: (store: IDBObjectStore) => IDBRequest<T>,
): Promise<T> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, mode);
    const store = tx.objectStore(STORE_NAME);
    const req = fn(store);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error ?? new Error('IndexedDB request failed'));
    tx.oncomplete = () => db.close();
  });
}

export async function loadDeviceIdentity(): Promise<DeviceIdentityRecord | null> {
  const raw = await withStore('readonly', (store) => store.get(RECORD_KEY));
  if (!raw || typeof raw !== 'object') return null;
  const rec = raw as Record<string, unknown>;
  if (typeof rec.device_id !== 'string' || typeof rec.device_secret !== 'string') return null;
  return {
    device_id: rec.device_id,
    device_secret: rec.device_secret,
    enrolled_at: typeof rec.enrolled_at === 'string' ? rec.enrolled_at : new Date().toISOString(),
  };
}

export async function saveDeviceIdentity(input: {
  readonly device_id: string;
  readonly device_secret: string;
}): Promise<void> {
  const record: DeviceIdentityRecord = {
    device_id: input.device_id.trim(),
    device_secret: input.device_secret,
    enrolled_at: new Date().toISOString(),
  };
  await withStore('readwrite', (store) => store.put(record, RECORD_KEY));
  await withStore('readwrite', (store) => store.put({ ever_enrolled: true }, HINT_KEY));
}

/** Indique qu'un enrôlement a déjà eu lieu sur ce navigateur (hint non autoritaire). */
export async function hadPriorDeviceEnrollment(): Promise<boolean> {
  const raw = await withStore('readonly', (store) => store.get(HINT_KEY));
  return Boolean(raw && typeof raw === 'object' && (raw as Record<string, unknown>).ever_enrolled);
}

export async function clearDeviceIdentity(): Promise<void> {
  await withStore('readwrite', (store) => store.delete(RECORD_KEY));
}

/** Efface credential et hint — tests / reset complet navigateur simulé. */
export async function clearAllDeviceIdentity(): Promise<void> {
  await withStore('readwrite', (store) => store.delete(RECORD_KEY));
  await withStore('readwrite', (store) => store.delete(HINT_KEY));
}

export async function hasDeviceIdentity(): Promise<boolean> {
  const rec = await loadDeviceIdentity();
  return Boolean(rec?.device_id && rec?.device_secret);
}

/** En-têtes API poste partagé — credential + device_id. */
export async function sharedWorkstationAuthHeaders(): Promise<Record<string, string>> {
  const identity = await loadDeviceIdentity();
  if (!identity) return {};
  return {
    'X-Recyclique-Device-Id': identity.device_id,
    'X-Recyclique-Device-Credential': identity.device_secret,
  };
}
