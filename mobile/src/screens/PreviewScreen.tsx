import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Linking } from 'react-native';

export default function PreviewScreen({ route, navigation }: any) {
  const { result } = route.params || {};

  if (!result) {
    return (
      <View style={s.center}>
        <Text style={s.empty}>No result to preview.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={s.container} contentContainerStyle={s.inner}>
      {/* Module badge */}
      {result.module_name && (
        <View style={s.badge}>
          <Text style={s.badgeTxt}>{result.module_name}</Text>
        </View>
      )}

      {/* Title */}
      <Text style={s.title}>{result.title || 'Result'}</Text>

      {/* Download buttons */}
      <View style={s.dlRow}>
        {result.pdf_url  && <DownloadBtn label="PDF"   url={result.pdf_url}  color="#ef4444" />}
        {result.docx_url && <DownloadBtn label="Word"  url={result.docx_url} color="#3b82f6" />}
        {result.pptx_url && <DownloadBtn label="Slides"url={result.pptx_url} color="#f59e0b" />}
        {result.xlsx_url && <DownloadBtn label="Excel" url={result.xlsx_url} color="#22c55e" />}
      </View>

      {/* Sections */}
      {(result.sections || []).map((sec: any, i: number) => (
        <View key={i} style={s.section}>
          <Text style={s.sectionHeading}>{sec.heading}</Text>
          <Text style={s.sectionContent}>{sec.content}</Text>
        </View>
      ))}

      {/* Generate more */}
      <TouchableOpacity style={s.backBtn} onPress={() => navigation.navigate('Generate', {})}>
        <Text style={s.backTxt}>✦ Generate Another</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

function DownloadBtn({ label, url, color }: { label: string; url: string; color: string }) {
  const API_BASE = 'https://easyai.app';
  const fullUrl  = url.startsWith('http') ? url : `${API_BASE}${url}`;
  return (
    <TouchableOpacity style={[s.dlBtn, { borderColor: color }]}
      onPress={() => Linking.openURL(fullUrl)}>
      <Text style={[s.dlTxt, { color }]}>⬇ {label}</Text>
    </TouchableOpacity>
  );
}

const s = StyleSheet.create({
  container:      { flex: 1, backgroundColor: '#0b1020' },
  center:         { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#0b1020' },
  inner:          { padding: 20, gap: 16 },
  badge:          { alignSelf: 'flex-start', backgroundColor: '#0f1729', borderWidth: 1,
                    borderColor: '#1e2d4a', borderRadius: 100, paddingHorizontal: 12, paddingVertical: 4 },
  badgeTxt:       { color: '#60a5fa', fontSize: 12, fontWeight: '600' },
  title:          { fontSize: 20, fontWeight: '800', color: '#e2e8f0' },
  dlRow:          { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  dlBtn:          { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 8, borderWidth: 1,
                    backgroundColor: '#0f1729' },
  dlTxt:          { fontSize: 13, fontWeight: '700' },
  section:        { backgroundColor: '#0f1729', borderRadius: 12, borderWidth: 1,
                    borderColor: '#1e2d4a', padding: 16, gap: 8 },
  sectionHeading: { fontSize: 14, fontWeight: '700', color: '#60a5fa' },
  sectionContent: { fontSize: 13, color: '#94a3b8', lineHeight: 20 },
  backBtn:        { backgroundColor: '#3b82f6', borderRadius: 12, padding: 16, alignItems: 'center',
                    marginTop: 8, marginBottom: 32 },
  backTxt:        { color: '#fff', fontWeight: '700', fontSize: 15 },
  empty:          { color: '#64748b' },
});
