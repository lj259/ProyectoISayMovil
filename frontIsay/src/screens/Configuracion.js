import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  ScrollView,
  View,
  Text,
  TouchableOpacity,
  Switch,
  StyleSheet,
  Alert
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = "http://192.168.1.140:8000";  // This is correct, keep it as is

export default function Configuracion({ navigation }) {
  const [usuario, setUsuario] = useState({
    nombre: '',
    email: '',
    telefono: ''
  });
  const [notifEmail, setNotifEmail] = useState(false);
  const [notifSms, setNotifSms] = useState(false);
  const [alertaPresupuesto, setAlertaPresupuesto] = useState(false);
  const [recordatorioPago, setRecordatorioPago] = useState(false);

  useEffect(() => {
    fetchPerfil();
  }, []);

  const fetchPerfil = async () => {
    try {
      // supongamos que tienes GET /usuarios/1
      const res = await fetch(`${API_URL}/usuarios/1`);
      const data = await res.json();
      setUsuario({
        nombre: data.nombre,
        email: data.email,
        telefono: data.telefono
      });
      // aquí podrías inicializar los toggles según data
    } catch (error) {
      console.log('Error cargando perfil', error);
      Alert.alert('Error', 'No se pudo cargar tu perfil');
    }
  };

  const handleLogout = async () => {
    // limpia token/id y vuelve a login
    await AsyncStorage.removeItem('userId');
    navigation.replace('Login');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.heading}>Configuración</Text>
        <Text style={styles.subheading}>Personaliza tu experiencia en Lana App</Text>

        {/* Perfil de usuario */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Perfil de usuario</Text>
            <TouchableOpacity onPress={() => navigation.navigate('EditarPerfil')}>
              <Text style={styles.editIcon}>✏️</Text>
            </TouchableOpacity>
          </View>
          <Text style={styles.label}>Nombre completo</Text>
          <Text style={styles.value}>{usuario.nombre}</Text>
          <Text style={styles.label}>Correo electrónico</Text>
          <Text style={styles.value}>{usuario.email}</Text>
          <Text style={styles.label}>Teléfono</Text>
          <Text style={styles.value}>{usuario.telefono}</Text>
        </View>

        {/* Notificaciones */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Notificaciones</Text>
          <View style={styles.row}>
            <Text style={styles.optionText}>Notificaciones por Email</Text>
            <Switch value={notifEmail} onValueChange={setNotifEmail} />
          </View>
          <View style={styles.row}>
            <Text style={styles.optionText}>Notificaciones por SMS</Text>
            <Switch value={notifSms} onValueChange={setNotifSms} />
          </View>
          <View style={styles.row}>
            <Text style={styles.optionText}>Alertas de Presupuesto</Text>
            <Switch value={alertaPresupuesto} onValueChange={setAlertaPresupuesto} />
          </View>
          <View style={styles.row}>
            <Text style={styles.optionText}>Recordatorios de Pago</Text>
            <Switch value={recordatorioPago} onValueChange={setRecordatorioPago} />
          </View>
        </View>

        {/* Información de la cuenta */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Información de la Cuenta</Text>
          <View style={styles.row}>
            <Text style={styles.infoLabel}>Usuario desde</Text>
            <Text style={styles.infoValue}>Enero 2025</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.infoLabel}>Última actividad</Text>
            <Text style={styles.infoValue}>Hoy</Text>
          </View>
        </View>

        {/* Cerrar sesión */}
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Cerrar Sesión</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  content: { padding: 16 },
  heading: { fontSize: 24, fontWeight: 'bold', textAlign: 'center' },
  subheading: { fontSize: 14, textAlign: 'center', marginBottom: 20, color: '#666' },
  card: {
    borderWidth: 1,
    borderColor: '#000',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardTitle: { fontSize: 16, fontWeight: 'bold' },
  editIcon: { fontSize: 18 },
  label: { fontSize: 14, color: '#333', marginTop: 8 },
  value: {
    fontSize: 14,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 4,
    padding: 8,
    marginTop: 4,
    color: '#000'
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 12
  },
  optionText: { fontSize: 14 },
  infoLabel: { fontSize: 14, color: '#333' },
  infoValue: { fontSize: 14, fontWeight: '600' },
  logoutButton: {
    backgroundColor: '#28a745',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10
  },
  logoutButtonText: { color: '#fff', fontWeight: 'bold' }
});
