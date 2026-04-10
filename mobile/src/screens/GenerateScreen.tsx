import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, Alert, ScrollView, Platform,
} from 'react-native';
import { launchCamera } from 'react-native-image-picker';
import { generate, uploadFile } from '../api/easyai';

const MODULES = [
  { id: 'auto',       label: '✦ Auto',        },
  { id: 'document',   label: '📄 Document'    },
  { id: 'slides',     label: '📽️ Slides'     },
  { id: 'excel',      label: '📊 Excel'       },
  { id: 'business',   label: '🏢 Business'    },
  { id: 'research',   label: '🔬 Research'    },
  { id: 'court',      label: '⚖️ Court'       },
  { id: 'exam',       label: '📝 Exam Prep'   },
  { id: 'course',     label: '🏫 Course'      },
];

export default function GenerateScreen({ route, navigation }: any) {
  const initialModule = route?.params?.module || 'auto';
  const [prompt,  setPrompt]  = useState('');
  const [module,  setModule]  = useState(initialModule);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) { Alert.alert('Error', 'Please enter a prompt.'); return; }
    setLoading(true);
    try {
      const result = await generate(prompt, module);
      navigation.navigate('Preview', { result });
    } catch (e: any) {
      Alert.alert('Error', e?.response?.data?.detail || e.message || 'Generation failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleCameraUpload = async () => {
    const res = await launchCamera({ mediaType: 'photo', quality: 0.8 });
    if (res.assets?.[0]) {
      setLoading(true);
      try {
        const asset = res.assets[0];
        const uploaded = await uploadFile(asset.uri!, asset.fileName || 'photo.jpg', asset.type || 'image/jpeg');
        if (uploaded.body) setPrompt(`Based on this document:\n\n${uploaded.body.substring(0, 1000)}`);
      } catch (e: any) {
        Alert.alert('Upload Error', e.message);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <ScrollView style={s.container} contentContainerStyle={s.inner} keyboardShouldPersistTaps="handled">
      <Text style={s.label}>Select AI Module</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.moduleScroll}>
        {MODULES.map((m) => (
          <TouchableOpacity key={m.id} style={[s.moduleBtn, module === m.id && s.moduleActive]}
            onPress={() => setModule(m.id)}>
            <Text style={[s.moduleTxt, module === m.id && s.moduleActiveTxt]}>{m.label}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <Text style={s.label}>Your Prompt</Text>
      <TextInput
        style={s.textarea}
        value={prompt}
        onChangeText={setPrompt}
        placeholder="Describe what you want Easy AI to generate…"
        placeholderTextColor="#4a6080"
        multiline
        numberOfLines={6}
        textAlignVertical="top"
      />

      <View style={s.buttonRow}>
        <TouchableOpacity style={s.cameraBtn} onPress={handleCameraUpload}>
          <Text style={s.cameraTxt}>📷 Photo</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[s.generateBtn, loading && s.disabled]}
          onPress={handleGenerate} disabled={loading}>
          {loading
            ? <ActivityIndicator color="#fff" />
            : <Text style={s.generateTxt}>✦ Generate</Text>}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  container:      { flex: 1, backgroundColor: '#0b1020' },
  inner:          { padding: 20, gap: 14 },
  label:          { color: '#94a3b8', fontSize: 12, fontWeight: '700', textTransform: 'uppercase',
                    letterSpacing: 0.8, marginBottom: 2 },
  moduleScroll:   { flexGrow: 0, marginBottom: 4 },
  moduleBtn:      { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 100, borderWidth: 1,
                    borderColor: '#1e2d4a', marginRight: 8, backgroundColor: '#0f1729' },
  moduleActive:   { backgroundColor: '#3b82f6', borderColor: '#3b82f6' },
  moduleTxt:      { color: '#64748b', fontSize: 13 },
  moduleActiveTxt:{ color: '#fff' },
  textarea:       { backgroundColor: '#0f1729', borderWidth: 1, borderColor: '#1e2d4a', borderRadius: 12,
                    padding: 14, color: '#e2e8f0', fontSize: 15, minHeight: 140 },
  buttonRow:      { flexDirection: 'row', gap: 12 },
  cameraBtn:      { flex: 0, paddingHorizontal: 16, paddingVertical: 16, backgroundColor: '#0f1729',
                    borderWidth: 1, borderColor: '#1e2d4a', borderRadius: 12, alignItems: 'center' },
  cameraTxt:      { color: '#94a3b8', fontSize: 14 },
  generateBtn:    { flex: 1, backgroundColor: '#3b82f6', borderRadius: 12, padding: 16, alignItems: 'center' },
  disabled:       { opacity: 0.6 },
  generateTxt:    { color: '#fff', fontWeight: '700', fontSize: 16 },
});
