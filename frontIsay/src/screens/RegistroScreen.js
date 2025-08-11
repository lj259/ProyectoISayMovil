import React, { useState } from 'react';
import { View, Text, TextInput, Button, Alert, StyleSheet } from 'react-native';
import { register } from '../utils/api';

export default function RegistroScreen({ navigation }) {
  const [form, setForm] = useState({
    nombre_usuario: '',
    correo: '',
    telefono: '',
    contraseña_hash: '',
    confirmar: ''
  });

  const handleRegister = async () => {
    if (form.contraseña_hash !== form.confirmar) {
      Alert.alert('Error', 'Las contraseñas no coinciden');
      return;
    }
    try {
      const res = await register(form);
      Alert.alert('Éxito', res.mensaje);
      navigation.navigate('Login');
    } catch (err) {
      Alert.alert('Error', err.response?.data?.detail || 'Algo salió mal');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.titulo}>App</Text>
      <Text style={styles.subtitulo}>REGÍSTRATE</Text>

      <TextInput style={styles.input} placeholder="Nombre" onChangeText={val => setForm({ ...form, nombre_usuario: val })} />
      <TextInput style={styles.input} placeholder="Correo electrónico" keyboardType="email-address" onChangeText={val => setForm({ ...form, correo: val })} />
      <TextInput style={styles.input} placeholder="Número de teléfono" keyboardType="phone-pad" onChangeText={val => setForm({ ...form, telefono: val })} />
      <TextInput style={styles.input} placeholder="Contraseña" secureTextEntry onChangeText={val => setForm({ ...form, contraseña_hash: val })} />
      <TextInput style={styles.input} placeholder="Confirmar contraseña" secureTextEntry onChangeText={val => setForm({ ...form, confirmar: val })} />

      <Button title="Registrar" onPress={handleRegister} color="#2e7d32" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center', backgroundColor: '#fff' },
  titulo: { textAlign: 'center', fontSize: 26, fontWeight: 'bold', marginBottom: 4 },
  subtitulo: { textAlign: 'center', fontSize: 18, marginBottom: 12 },
  input: { borderWidth: 1, borderColor: '#ccc', padding: 10, marginBottom: 10, borderRadius: 6 }
});
