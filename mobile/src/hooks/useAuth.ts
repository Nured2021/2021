import { useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const TOKEN_KEY = 'easy_ai_token';
const USER_KEY  = 'easy_ai_user';

interface User {
  id:    string;
  email: string;
  name:  string;
  role:  string;
  plan:  string;
}

export function useAuth() {
  const [user,  setUser]  = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    AsyncStorage.getItem(USER_KEY).then((raw) => {
      if (raw) setUser(JSON.parse(raw));
      setReady(true);
    });
  }, []);

  const saveUser = useCallback(async (u: User, token: string) => {
    await AsyncStorage.setItem(USER_KEY,  JSON.stringify(u));
    await AsyncStorage.setItem(TOKEN_KEY, token);
    setUser(u);
  }, []);

  const logoutUser = useCallback(async () => {
    await AsyncStorage.multiRemove([USER_KEY, TOKEN_KEY]);
    setUser(null);
  }, []);

  return { user, ready, saveUser, logoutUser };
}
