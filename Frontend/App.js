import React, { useState } from 'react';
import { StyleSheet, Text, View, Image, ActivityIndicator, Alert, ScrollView, TouchableOpacity } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

// ⚠️ UPDATE THIS WITH YOUR CURRENT NGROK URL
const API_URL = 'https://kelley-overpolitic-pactionally.ngrok-free.dev/predict'; 

export default function App() {
  const [imageUri, setImageUri] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const pickImage = async () => {
    let res = await ImagePicker.launchImageLibraryAsync({ 
      allowsEditing: true, 
      aspect: [1, 1], 
      quality: 0.8 
    });
    if (!res.canceled) { 
      setImageUri(res.assets[0].uri); 
      setResult(null); 
    }
  };

  const startAnalysis = async () => {
    if (!imageUri) return;
    setLoading(true);
    let formData = new FormData();
    formData.append('file', { uri: imageUri, name: 'upload.jpg', type: 'image/jpeg' });
    try {
      let response = await fetch(API_URL, { method: 'POST', body: formData });
      let data = await response.json();
      if (data.status === 'success') setResult(data);
    } catch (e) { 
      Alert.alert("Connection Error", "Check your Ngrok and Server status."); 
    } finally { setLoading(false); }
  };

  return (
    <View style={styles.darkWrapper}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>DERM AI <Text style={{fontWeight: '300'}}>User Dashboard</Text></Text>
        </View>

        <View style={styles.dashboard}>
          {/* 1. UPLOAD SECTION */}
          <View style={styles.sectionCard}>
            <Text style={styles.sectionLabel}>User Image Upload</Text>
            <TouchableOpacity style={styles.uploadBox} onPress={pickImage}>
              {imageUri ? (
                <Image source={{ uri: imageUri }} style={styles.previewImage} />
              ) : (
                <Text style={styles.uploadText}>📸 Select User Skin Sample</Text>
              )}
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.analyzeBtn, (!imageUri || loading) && {opacity: 0.6}]} 
              onPress={startAnalysis} 
              disabled={loading || !imageUri}
            >
              {loading ? (
                <View style={{flexDirection: 'row', alignItems: 'center'}}>
                  <ActivityIndicator color="#0F1113" style={{marginRight: 10}} />
                  <Text style={styles.analyzeBtnText}>Processing XAI...</Text>
                </View>
              ) : (
                <Text style={styles.analyzeBtnText}>Perform Analysis</Text>
              )}
            </TouchableOpacity>
          </View>

          {/* 2. RESULTS SECTION */}
          {result && (
            <View>
              {/* Diagnosis Overview */}
              <View style={styles.sectionCard}>
                <Text style={styles.sectionLabel}>AI Diagnosis Result</Text>
                <Text style={styles.classResult}>✅ {result.prediction_name}</Text>
                <Text style={styles.confidenceText}>System Confidence: {result.confidence}%</Text>
              </View>

              {/* Heatmap Visualization */}
              <View style={styles.sectionCard}>
                <Text style={styles.sectionLabel}>XAI Segmentation (LIME)</Text>
                <View style={styles.xaiRow}>
                  <View style={styles.xaiColumn}>
                    <Image source={{ uri: imageUri }} style={styles.xaiImage} />
                    <Text style={styles.caption}>User Input</Text>
                  </View>
                  <View style={styles.xaiColumn}>
                    <Image 
                      source={{ uri: `${result.heatmap_url}?t=${new Date().getTime()}` }} 
                      style={styles.xaiImage} 
                    />
                    <Text style={styles.caption}>LIME Map</Text>
                  </View>
                </View>
              </View>

              {/* 🔥 RE-INSERTED: XAI Logic Breakdown */}
              <View style={styles.sectionCard}>
                <Text style={styles.sectionLabel}>XAI Logic Breakdown</Text>
                <Text style={styles.bulletPoint}>• {result.textual_explanation}</Text>
                <Text style={styles.bulletPoint}>• {result.precautions}</Text>
              </View>

              {/* Clinical Hygiene Section */}
              <View style={styles.sectionCard}>
                <Text style={styles.sectionLabel}>Clinical Hygiene & Prep</Text>
                <Text style={styles.hygieneIntro}>Protocol for professional consultation:</Text>
                
                <View style={styles.hygieneItem}>
                  <Text style={styles.hygieneText}>• Wash gently with mild soap. Avoid makeup, concealers, or moisturizers on the area before your exam.</Text>
                </View>
                <View style={styles.hygieneItem}>
                  <Text style={styles.hygieneText}>• Do not pick or scratch the lesion; this can distort texture analysis and cause secondary infection.</Text>
                </View>
                <View style={styles.hygieneItem}>
                  <Text style={styles.hygieneText}>• Take weekly follow-up photos in the same room lighting to track visual evolution for your doctor.</Text>
                </View>

                {/* Transparency Notice */}
                <View style={styles.transparencyNotice}>
                  <Text style={styles.noticeText}>
                    ⚠️ TRANSPARENCY NOTICE: This tool provides decision support, not remedies. 
                    No treatment is prescribed here. Clinical diagnosis requires a professional biopsy.
                  </Text>
                </View>
              </View>
            </View>
          )}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  darkWrapper: { flex: 1, backgroundColor: '#0F1113' },
  container: { paddingBottom: 50 },
  header: { padding: 20, paddingTop: 50, borderBottomWidth: 1, borderBottomColor: '#242629' },
  headerTitle: { color: '#E1E3E6', fontSize: 20, fontWeight: 'bold' },
  dashboard: { padding: 15 },
  sectionCard: { backgroundColor: '#1A1C1E', borderRadius: 12, padding: 18, marginBottom: 15, borderWidth: 1, borderColor: '#2D3034' },
  sectionLabel: { color: '#8E9196', fontSize: 11, fontWeight: 'bold', marginBottom: 12, textTransform: 'uppercase' },
  uploadBox: { height: 220, borderRadius: 10, borderStyle: 'dashed', borderWidth: 2, borderColor: '#3E4247', justifyContent: 'center', alignItems: 'center', backgroundColor: '#131517' },
  uploadText: { color: '#8E9196', fontSize: 13 },
  previewImage: { width: '100%', height: '100%', borderRadius: 8 },
  analyzeBtn: { backgroundColor: '#76E094', padding: 18, borderRadius: 8, marginTop: 15, alignItems: 'center' },
  analyzeBtnText: { color: '#0F1113', fontWeight: 'bold', fontSize: 16 },
  classResult: { color: '#76E094', fontSize: 22, fontWeight: 'bold' },
  confidenceText: { color: '#8E9196', marginTop: 5, fontSize: 14 },
  xaiRow: { flexDirection: 'row', justifyContent: 'space-between' },
  xaiColumn: { width: '48%', alignItems: 'center' },
  xaiImage: { width: '100%', height: 130, borderRadius: 8, backgroundColor: '#000' },
  caption: { color: '#8E9196', fontSize: 10, marginTop: 6, textTransform: 'uppercase' },
  bulletPoint: { color: '#E1E3E6', fontSize: 14, lineHeight: 22, marginBottom: 10 },
  hygieneIntro: { color: '#E1E3E6', fontSize: 13, marginBottom: 10, fontStyle: 'italic' },
  hygieneItem: { marginBottom: 10 },
  hygieneText: { color: '#8E9196', fontSize: 12, lineHeight: 18 },
  transparencyNotice: { marginTop: 15, padding: 12, backgroundColor: 'rgba(255, 193, 7, 0.1)', borderRadius: 8, borderWidth: 1, borderColor: 'rgba(255, 193, 7, 0.3)' },
  noticeText: { color: '#FFC107', fontSize: 10, textAlign: 'center', fontWeight: 'bold' }
});