import AsyncStorage from '@react-native-async-storage/async-storage';

const OFFLINE_KEY = 'easyai_offline_queue';

interface OfflineItem {
  id:        string;
  payload:   object;
  timestamp: number;
}

export async function saveOffline(payload: object): Promise<void> {
  const raw  = await AsyncStorage.getItem(OFFLINE_KEY);
  const queue: OfflineItem[] = raw ? JSON.parse(raw) : [];
  queue.push({ id: String(Date.now()), payload, timestamp: Date.now() });
  await AsyncStorage.setItem(OFFLINE_KEY, JSON.stringify(queue));
}

export async function getOfflineQueue(): Promise<OfflineItem[]> {
  const raw = await AsyncStorage.getItem(OFFLINE_KEY);
  return raw ? JSON.parse(raw) : [];
}

export async function clearOfflineQueue(): Promise<void> {
  await AsyncStorage.setItem(OFFLINE_KEY, '[]');
}
