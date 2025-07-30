import React, { useState } from 'react';
import { View, Text, TextInput, Button, Alert, TouchableOpacity, StyleSheet } from 'react-native';
import axios from 'axios';

const API_URL = 'http://localhost:8000'; 

export default function LoginScreen({ navigation }) {
  const [correo, setCorreo] = useState('');
  const [password, setContraseña] = useState('');

  const handleLogin = async () => {
    try {
      const res = await axios.post(`${API_URL}/login`, { correo, password });
      Alert.alert('Bienvenido', `${res.data.nombre_usuario}`);
    } catch (err) {
      Alert.alert('Error', err.response?.data?.detail || 'Error al iniciar sesión');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>Lana App</Text>
      <Text style={styles.subtitulo}>INICIO DE SESIÓN</Text>

      <TextInput style={styles.input} placeholder="Correo electrónico" keyboardType="email-address" onChangeText={setCorreo} />
      <TextInput style={styles.input} placeholder="Contraseña" secureTextEntry onChangeText={setContraseña} />

      <Button title="Iniciar sesión" onPress={handleLogin} color="#2e7d32" />

      <TouchableOpacity onPress={() => navigation.navigate('Registro')} style={{ marginTop: 10 }}>
        <Text style={styles.link}>¿No tienes cuenta? <Text style={{ color: '#007bff' }}>Regístrate</Text></Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center', backgroundColor: '#fff' },
  logo: { textAlign: 'center', fontSize: 30, fontWeight: 'bold', color: '#2e7d32', marginBottom: 10 },
  subtitulo: { textAlign: 'center', fontSize: 18, marginBottom: 14 },
  input: { borderWidth: 1, borderColor: '#ccc', padding: 10, marginBottom: 10, borderRadius: 6 },
  link: { textAlign: 'center', fontSize: 14 }
});
