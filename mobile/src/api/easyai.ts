import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const API_BASE = 'https://easyai.app';   // change to your deployed URL

const client = axios.create({ baseURL: API_BASE, timeout: 30000 });

// Attach auth token on every request
client.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('easy_ai_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function login(email: string, password: string) {
  const { data } = await client.post('/auth/login', { email, password });
  await AsyncStorage.setItem('easy_ai_token', data.token);
  return data.user;
}

export async function signup(email: string, password: string, name: string, role = 'student') {
  const { data } = await client.post('/auth/signup', { email, password, name, role });
  await AsyncStorage.setItem('easy_ai_token', data.token);
  return data.user;
}

export async function logout() {
  await AsyncStorage.removeItem('easy_ai_token');
}

export async function generate(prompt: string, module = 'auto') {
  const { data } = await client.post('/api/build', { prompt, module });
  return data;
}

export async function uploadFile(uri: string, filename: string, mimeType: string) {
  const form = new FormData();
  form.append('file', { uri, name: filename, type: mimeType } as any);
  const { data } = await client.post('/api/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function getDashboard() {
  const { data } = await client.get('/api/dashboard');
  return data;
}
