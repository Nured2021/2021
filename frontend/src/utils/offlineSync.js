/**
 * Offline queue utilities for Easy AI.
 *
 * When the user generates content while offline:
 *   1. `saveOffline(payload)` persists the request in IndexedDB.
 *   2. When connectivity is restored, `syncOffline()` replays the queue.
 *   3. A 'online' event listener auto-triggers the sync.
 *
 * The service worker also registers a background-sync tag ('sync-offline-queue')
 * for environments that support the Background Sync API.
 */

const DB_NAME    = 'easyai-offline';
const DB_VERSION = 1;
const STORE_NAME = 'queue';

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (e) => {
      e.target.result.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
    };
    req.onsuccess = (e) => resolve(e.target.result);
    req.onerror   = (e) => reject(e.target.error);
  });
}

function idbRequest(req) {
  return new Promise((resolve, reject) => {
    req.onsuccess = (e) => resolve(e.target.result);
    req.onerror   = (e) => reject(e.target.error);
  });
}

/**
 * Save a generation payload to the offline queue.
 * @param {object} payload  The /api/build request body.
 * @param {object} [localResult]  Optional local preview result.
 */
export async function saveOffline(payload, localResult = null) {
  const db   = await openDB();
  const tx   = db.transaction(STORE_NAME, 'readwrite');
  const store = tx.objectStore(STORE_NAME);
  await idbRequest(store.add({ payload, localResult, timestamp: Date.now() }));
}

/**
 * Flush every item in the offline queue by replaying it against the API.
 */
export async function syncOffline() {
  if (!navigator.onLine) return;

  const db    = await openDB();
  const tx    = db.transaction(STORE_NAME, 'readwrite');
  const store = tx.objectStore(STORE_NAME);
  const items = await idbRequest(store.getAll());

  for (const item of items) {
    try {
      const token = localStorage.getItem('easy_ai_token');
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const response = await fetch('/api/build', {
        method:  'POST',
        headers,
        body: JSON.stringify(item.payload),
      });

      if (response.ok) {
        // Remove synced item
        const delTx  = db.transaction(STORE_NAME, 'readwrite');
        const delSt  = delTx.objectStore(STORE_NAME);
        delSt.delete(item.id);
        console.log('[OfflineSync] Synced item', item.id);
      }
    } catch (err) {
      console.warn('[OfflineSync] Failed to sync item', item.id, err);
    }
  }
}

/**
 * Return how many items are pending in the offline queue.
 */
export async function offlineQueueLength() {
  const db    = await openDB();
  const tx    = db.transaction(STORE_NAME, 'readonly');
  const store = tx.objectStore(STORE_NAME);
  return idbRequest(store.count());
}

// Auto-sync when browser comes back online
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    console.log('[OfflineSync] Back online — syncing queue…');
    syncOffline().catch(console.warn);

    // Also trigger background sync if supported
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      navigator.serviceWorker.ready
        .then((reg) => reg.sync.register('sync-offline-queue'))
        .catch(console.warn);
    }
  });
}
