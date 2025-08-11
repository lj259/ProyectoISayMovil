// src/screens/Register.js
import React, { useState } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Platform
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const LOCALHOST = Platform.OS === 'android'
  // Android emulator → 10.0.2.2
  ? 'http://10.0.2.2:8000'
  // Dispositivo físico o iOS simulator → tu IP de red local
  : 'http://192.168.1.65:8000';

export default function Register({ navigation }) {
  const [nombre, setNombre] = useState('');
  const [correo, setCorreo] = useState('');
  const [contraseña, setContraseña] = useState('');

  const handleRegister = async () => {
    if (!nombre || !correo || contraseña.length < 6) {
      Alert.alert(
        'Error de validación',
        'Completa todos los campos; contraseña mínimo 6 caracteres'
      );
      return;
    }

    try {
      const res = await fetch(`${LOCALHOST}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nombre_usuario: nombre,
          correo,
          contraseña
        })
      });

      if (!res.ok) {
        // captura status y cuerpo para debug
        const text = await res.text();
        console.error('Registro fallido', res.status, text);
        Alert.alert(
          'Error',
          `No se pudo registrar (status ${res.status})`
        );
        return;
      }

      const data = await res.json();
      await AsyncStorage.setItem('userId', data.id.toString());
      navigation.replace('Main');

    } catch (e) {
      console.error('Fetch error', e);
      Alert.alert(
        'Error de conexión',
        'No se pudo conectar al servidor'
      );
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.form}>
        <Text style={styles.title}>Registrarse</Text>
        <TextInput
          style={styles.input}
          placeholder="Usuario"
          value={nombre}
          onChangeText={setNombre}
        />
        <TextInput
          style={styles.input}
          placeholder="Correo"
          value={correo}
          onChangeText={setCorreo}
          keyboardType="email-address"
        />
        <TextInput
          style={styles.input}
          placeholder="Contraseña"
          value={contraseña}
          onChangeText={setContraseña}
          secureTextEntry
        />
        <TouchableOpacity style={styles.button} onPress={handleRegister}>
          <Text style={styles.btnText}>Crear Cuenta</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.link}>Volver a Login</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 16 },
  form: { backgroundColor: '#fff', padding: 20, borderRadius: 8, elevation: 3 },
  title: {
    fontSize: 20, fontWeight: 'bold', marginBottom: 12, textAlign: 'center'
  },
  input: {
    borderWidth: 1, borderColor: '#ccc', borderRadius: 6,
    padding: 8, marginBottom: 12
  },
  button: {
    backgroundColor: '#2ecc71', padding: 12,
    borderRadius: 6, alignItems: 'center', marginBottom: 8
  },
  btnText: { color: '#fff', fontWeight: 'bold' },
  link: { color: '#2980b9', textAlign: 'center', marginTop: 8 }
});
