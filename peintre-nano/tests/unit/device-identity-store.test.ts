// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  clearAllDeviceIdentity,
  clearDeviceIdentity,
  hadPriorDeviceEnrollment,
  hasDeviceIdentity,
  loadDeviceIdentity,
  saveDeviceIdentity,
} from '../../src/domains/shared-workstation/device-identity-store';

type StoreRecord = Record<string, unknown>;

const memoryStore = new Map<string, StoreRecord>();

function makeRequest<T>(result: T): IDBRequest<T> {
  const req = {
    result,
    error: null as DOMException | null,
    onsuccess: null as ((ev: Event) => void) | null,
    onerror: null as ((ev: Event) => void) | null,
  } as IDBRequest<T>;
  queueMicrotask(() => req.onsuccess?.(new Event('success')));
  return req;
}

function installIndexedDbMock() {
  memoryStore.clear();
  vi.stubGlobal('indexedDB', {
    open: () => {
      const db = {
        objectStoreNames: { contains: () => false },
        createObjectStore: () => ({}),
        transaction: () => ({
          objectStore: () => ({
            get: (key: IDBValidKey) => makeRequest(memoryStore.get(String(key))),
            put: (value: StoreRecord, key: IDBValidKey) => {
              memoryStore.set(String(key), value);
              return makeRequest(key);
            },
            delete: (key: IDBValidKey) => {
              memoryStore.delete(String(key));
              return makeRequest(undefined);
            },
          }),
        }),
        close: () => undefined,
      } as unknown as IDBDatabase;
      const req = {
        result: db,
        onsuccess: null as ((ev: Event) => void) | null,
        onupgradeneeded: null as ((ev: IDBOpenDBRequestEventMap['upgradeneeded']) => void) | null,
      } as IDBOpenDBRequest;
      queueMicrotask(() => {
        req.onupgradeneeded?.({ target: req } as IDBVersionChangeEvent);
        req.onsuccess?.(new Event('success'));
      });
      return req;
    },
  });
}

describe('device-identity-store', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
    vi.spyOn(Storage.prototype, 'setItem');
    installIndexedDbMock();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('save/load/clear via IndexedDB without localStorage', async () => {
    await saveDeviceIdentity({ device_id: 'd1', device_secret: 'secret-abc' });
    expect(localStorage.setItem).not.toHaveBeenCalled();
    expect(await hasDeviceIdentity()).toBe(true);
    expect(await hadPriorDeviceEnrollment()).toBe(true);
    const loaded = await loadDeviceIdentity();
    expect(loaded?.device_id).toBe('d1');
    expect(loaded?.device_secret).toBe('secret-abc');
    await clearDeviceIdentity();
    expect(await hasDeviceIdentity()).toBe(false);
    expect(await hadPriorDeviceEnrollment()).toBe(true);
    await clearAllDeviceIdentity();
    expect(await hadPriorDeviceEnrollment()).toBe(false);
  });
});
