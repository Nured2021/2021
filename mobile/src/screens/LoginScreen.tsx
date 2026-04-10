import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, Alert, ScrollView, KeyboardAvoidingView, Platform,
} from 'react-native';
import { login, signup } from '../api/easyai';

const ROLES = ['student', 'teacher', 'professor', 'lawyer', 'admin'];

export default function LoginScreen({ navigation }: any) {
  const [isLogin, setIsLogin]   = useState(true);
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [name, setName]         = useState('');
  const [role, setRole]         = useState('student');
  const [loading, setLoading]   = useState(false);

  const handleSubmit = async () => {
    if (!email || !password) { Alert.alert('Error', 'Email and password required.'); return; }
    setLoading(true);
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        if (!name) { Alert.alert('Error', 'Name required.'); return; }
        await signup(email, password, name, role);
      }
      navigation.replace('Dashboard');
    } catch (e: any) {
      Alert.alert('Error', e?.response?.data?.detail || e.message || 'Authentication failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={s.container} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView contentContainerStyle={s.inner}>
        <Text style={s.logo}>✦ Easy AI</Text>
        <Text style={s.tagline}>Your 17-module AI workspace</Text>

        <View style={s.card}>
          <Text style={s.heading}>{isLogin ? 'Sign In' : 'Create Account'}</Text>

          {!isLogin && (
            <TextInput style={s.input} placeholder="Full Name" placeholderTextColor="#4a6080"
              value={name} onChangeText={setName} />
          )}

          <TextInput style={s.input} placeholder="Email" placeholderTextColor="#4a6080"
            value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />

          <TextInput style={s.input} placeholder="Password" placeholderTextColor="#4a6080"
            value={password} onChangeText={setPassword} secureTextEntry />

          {!isLogin && (
            <View style={s.roleRow}>
              {ROLES.map((r) => (
                <TouchableOpacity key={r} style={[s.roleBtn, role === r && s.roleActive]}
                  onPress={() => setRole(r)}>
                  <Text style={[s.roleTxt, role === r && s.roleActiveTxt]}>{r}</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}

          <TouchableOpacity style={s.btn} onPress={handleSubmit} disabled={loading}>
            {loading ? <ActivityIndicator color="#fff" /> :
              <Text style={s.btnTxt}>{isLogin ? 'Sign In' : 'Sign Up'}</Text>}
          </TouchableOpacity>

          <TouchableOpacity onPress={() => setIsLogin(!isLogin)}>
            <Text style={s.switchTxt}>
              {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const s = StyleSheet.create({
  container:  { flex: 1, backgroundColor: '#0b1020' },
  inner:      { flexGrow: 1, justifyContent: 'center', padding: 24 },
  logo:       { fontSize: 32, fontWeight: '800', color: '#60a5fa', textAlign: 'center', marginBottom: 4 },
  tagline:    { color: '#64748b', textAlign: 'center', marginBottom: 32 },
  card:       { backgroundColor: '#0f1729', borderRadius: 16, padding: 24, borderWidth: 1, borderColor: '#1e2d4a' },
  heading:    { fontSize: 20, fontWeight: '700', color: '#e2e8f0', marginBottom: 20 },
  input:      { backgroundColor: '#0b1020', borderWidth: 1, borderColor: '#1e2d4a', borderRadius: 10,
                padding: 14, color: '#e2e8f0', marginBottom: 12, fontSize: 15 },
  roleRow:    { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 16 },
  roleBtn:    { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 100, borderWidth: 1, borderColor: '#1e2d4a' },
  roleActive: { backgroundColor: '#3b82f6', borderColor: '#3b82f6' },
  roleTxt:    { color: '#64748b', fontSize: 13, textTransform: 'capitalize' },
  roleActiveTxt: { color: '#fff' },
  btn:        { backgroundColor: '#3b82f6', borderRadius: 10, padding: 16, alignItems: 'center', marginBottom: 16 },
  btnTxt:     { color: '#fff', fontWeight: '700', fontSize: 16 },
  switchTxt:  { color: '#60a5fa', textAlign: 'center', fontSize: 14 },
});
