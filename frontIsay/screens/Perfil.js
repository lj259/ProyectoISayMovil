import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  ScrollView,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const API_URL = "http://192.168.1.65:8000";

export default function Perfil({ navigation }) {
  const [usuario, setUsuario] = useState({
    nombre: '',
    email: '',
    telefono: ''
  });

  useEffect(() => {
    fetchPerfil();
  }, []);

  const fetchPerfil = async () => {
    try {
      const res = await fetch(`${API_URL}/usuarios/1`);
      const data = await res.json();
      setUsuario({
        nombre: data.nombre,
        email: data.email,
        telefono: data.telefono
      });
    } catch (error) {
      console.log('Error cargando perfil', error);
      Alert.alert('Error', 'No se pudo cargar tu perfil');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.card}>
          <View style={styles.header}>
            <Text style={styles.title}>Mi Perfil</Text>
            <View style={styles.icons}>
              <TouchableOpacity onPress={() => navigation.navigate('EditarPerfil')}>
                <Ionicons name="pencil" size={24} style={styles.icon} />
              </TouchableOpacity>
              <TouchableOpacity onPress={() => navigation.navigate('Configuracion')}>
                <Ionicons name="settings" size={24} />
              </TouchableOpacity>
            </View>
          </View>

          <Text style={styles.label}>Nombre completo</Text>
          <Text style={styles.value}>{usuario.nombre}</Text>

          <Text style={styles.label}>Correo electrónico</Text>
          <Text style={styles.value}>{usuario.email}</Text>

          <Text style={styles.label}>Teléfono</Text>
          <Text style={styles.value}>{usuario.telefono}</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  content: { padding: 16 },
  card: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 16
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  title: { fontSize: 18, fontWeight: 'bold' },
  icons: { flexDirection: 'row' },
  icon: { marginRight: 16 },
  label: { fontSize: 14, marginTop: 12, fontWeight: '600' },
  value: {
    fontSize: 14,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    padding: 8,
    marginTop: 4,
    color: '#000'
  }
});
