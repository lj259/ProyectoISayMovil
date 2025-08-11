import React, { useState } from 'react';
import { View, Text, TextInput, Button, Alert, TouchableOpacity, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { login } from '../utils/api'; 

export default function LoginScreen() {

  const [correo, setCorreo] = useState('');
  const [contraseña_hash, setContraseña] = useState('');
  const navigation = useNavigation();

  const handleLogin = async () => {
    try {
      console.log(`Iniciando sesión con correo: ${correo}`,' y contraseña: ', contraseña_hash);
      const res = await login(correo, contraseña_hash);
      Alert.alert('Bienvenido', `${res.nombre_usuario}`);
      navigation.navigate('Home'); 
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
