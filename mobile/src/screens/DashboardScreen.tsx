import React, { useEffect, useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  ActivityIndicator, RefreshControl,
} from 'react-native';
import { getDashboard } from '../api/easyai';

const ROLE_ICONS: Record<string, string> = {
  student: '🙋', teacher: '📚', professor: '🎓',
  lawyer: '⚖️', admin: '👑',
};

export default function DashboardScreen({ navigation }: any) {
  const [data, setData]         = useState<any>(null);
  const [loading, setLoading]   = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = async (refresh = false) => {
    if (refresh) setRefreshing(true); else setLoading(true);
    try {
      const d = await getDashboard();
      setData(d);
    } catch (e) {
      console.warn('Dashboard load error', e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <View style={s.center}>
        <ActivityIndicator size="large" color="#60a5fa" />
      </View>
    );
  }

  const role = data?.role || 'student';
  const icon = ROLE_ICONS[role] || '🙋';

  return (
    <ScrollView style={s.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => load(true)} tintColor="#60a5fa" />}
    >
      {/* Hero */}
      <View style={s.hero}>
        <Text style={s.heroIcon}>{icon}</Text>
        <Text style={s.heroTitle}>{role.charAt(0).toUpperCase() + role.slice(1)} Dashboard</Text>
        <Text style={s.heroSub}>Plan: {data?.stats?.plan?.toUpperCase() || '—'}</Text>
      </View>

      {/* Stats */}
      <View style={s.statsRow}>
        <View style={s.stat}>
          <Text style={s.statVal}>{data?.stats?.total_generated ?? 0}</Text>
          <Text style={s.statLbl}>Generated</Text>
        </View>
        <View style={s.stat}>
          <Text style={s.statVal}>{data?.recent_documents?.length ?? 0}</Text>
          <Text style={s.statLbl}>Documents</Text>
        </View>
        <View style={s.stat}>
          <Text style={s.statVal}>{data?.recommended_modules?.length ?? 0}</Text>
          <Text style={s.statLbl}>Tools</Text>
        </View>
      </View>

      {/* Quick actions */}
      <Text style={s.sectionTitle}>AI Tools</Text>
      <View style={s.grid}>
        {(data?.recommended_modules || []).map((m: any) => (
          <TouchableOpacity key={m.id} style={s.modCard}
            onPress={() => navigation.navigate('Generate', { module: m.id })}>
            <Text style={s.modIcon}>{m.icon}</Text>
            <Text style={s.modName}>{m.name}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Recent docs */}
      {data?.recent_documents?.length > 0 && (
        <>
          <Text style={s.sectionTitle}>Recent Documents</Text>
          {data.recent_documents.map((d: any) => (
            <View key={d.id} style={s.docRow}>
              <Text style={s.docTitle} numberOfLines={1}>{d.title}</Text>
              <Text style={s.docMeta}>{d.module}</Text>
            </View>
          ))}
        </>
      )}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const s = StyleSheet.create({
  container:   { flex: 1, backgroundColor: '#0b1020' },
  center:      { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#0b1020' },
  hero:        { alignItems: 'center', padding: 28, borderBottomWidth: 1, borderColor: '#1e2d4a' },
  heroIcon:    { fontSize: 40, marginBottom: 8 },
  heroTitle:   { fontSize: 20, fontWeight: '800', color: '#e2e8f0' },
  heroSub:     { color: '#60a5fa', marginTop: 4, fontSize: 13 },
  statsRow:    { flexDirection: 'row', borderBottomWidth: 1, borderColor: '#1e2d4a' },
  stat:        { flex: 1, alignItems: 'center', padding: 16, borderRightWidth: 1, borderColor: '#1e2d4a' },
  statVal:     { fontSize: 22, fontWeight: '800', color: '#60a5fa' },
  statLbl:     { fontSize: 11, color: '#64748b', marginTop: 2, textTransform: 'uppercase' },
  sectionTitle:{ padding: 16, paddingBottom: 8, fontSize: 13, fontWeight: '700', color: '#94a3b8',
                 textTransform: 'uppercase', letterSpacing: 1 },
  grid:        { flexDirection: 'row', flexWrap: 'wrap', paddingHorizontal: 12, gap: 10 },
  modCard:     { width: '30%', backgroundColor: '#0f1729', borderRadius: 12, borderWidth: 1,
                 borderColor: '#1e2d4a', padding: 14, alignItems: 'center', gap: 6 },
  modIcon:     { fontSize: 24 },
  modName:     { fontSize: 11, color: '#94a3b8', textAlign: 'center' },
  docRow:      { marginHorizontal: 16, marginBottom: 8, backgroundColor: '#0f1729', borderRadius: 10,
                 borderWidth: 1, borderColor: '#1e2d4a', padding: 12 },
  docTitle:    { color: '#e2e8f0', fontSize: 14, fontWeight: '600' },
  docMeta:     { color: '#64748b', fontSize: 12, marginTop: 2, textTransform: 'capitalize' },
});
