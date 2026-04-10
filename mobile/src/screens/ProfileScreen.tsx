import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, ScrollView } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { logout } from '../api/easyai';

export default function ProfileScreen({ navigation }: any) {
  const [loading, setLoading] = useState(false);

  const handleLogout = async () => {
    setLoading(true);
    try {
      await logout();
      navigation.replace('Login');
    } catch (e) {
      Alert.alert('Error', 'Logout failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={s.container} contentContainerStyle={s.inner}>
      <View style={s.section}>
        <Text style={s.sectionTitle}>Account</Text>
        <TouchableOpacity style={s.row} onPress={handleLogout} disabled={loading}>
          <Text style={s.rowIcon}>⏏</Text>
          <Text style={s.rowLabel}>{loading ? 'Signing out…' : 'Sign Out'}</Text>
        </TouchableOpacity>
      </View>

      <View style={s.section}>
        <Text style={s.sectionTitle}>About</Text>
        <View style={s.row}>
          <Text style={s.rowIcon}>✦</Text>
          <Text style={s.rowLabel}>Easy AI Mobile v1.0.0</Text>
        </View>
        <View style={s.row}>
          <Text style={s.rowIcon}>🤖</Text>
          <Text style={s.rowLabel}>17 specialist AI modules</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  container:    { flex: 1, backgroundColor: '#0b1020' },
  inner:        { padding: 20, gap: 20 },
  section:      { backgroundColor: '#0f1729', borderRadius: 14, borderWidth: 1,
                  borderColor: '#1e2d4a', overflow: 'hidden' },
  sectionTitle: { padding: 14, paddingBottom: 8, fontSize: 12, fontWeight: '700',
                  color: '#64748b', textTransform: 'uppercase', letterSpacing: 0.8 },
  row:          { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 16,
                  borderTopWidth: 1, borderColor: '#1e2d4a' },
  rowIcon:      { fontSize: 18 },
  rowLabel:     { fontSize: 15, color: '#e2e8f0' },
});
