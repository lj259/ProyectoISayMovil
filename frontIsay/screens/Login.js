import React, { useState } from 'react';
import { SafeAreaView, View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://192.168.1.65:8000';
export default function Login({ navigation }) {
  const [correo, setCorreo] = useState('');
  const [contraseña, setContraseña] = useState('');

  const handleLogin = async () => {
    if (!correo || !contraseña) { Alert.alert('Error', 'Completa todos los campos'); return; }
    try {
      const res = await fetch(`${API_URL}/login`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo, contraseña })
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      await AsyncStorage.setItem('userId', data.usuario_id.toString());
      navigation.replace('Main');
    } catch {
      Alert.alert('Error', 'Credenciales incorrectas');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.form}>
        <Text style={styles.title}>Iniciar Sesión</Text>
        <TextInput style={styles.input} placeholder="Correo" value={correo} onChangeText={setCorreo} keyboardType="email-address" />
        <TextInput style={styles.input} placeholder="Contraseña" value={contraseña} onChangeText={setContraseña} secureTextEntry />
        <TouchableOpacity style={styles.button} onPress={handleLogin}><Text style={styles.btnText}>Entrar</Text></TouchableOpacity>
        <TouchableOpacity onPress={() => navigation.navigate('Register')}><Text style={styles.link}>Registrarse</Text></TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex:1, justifyContent:'center', padding:16 },
  form: { backgroundColor:'#fff', padding:20, borderRadius:8, elevation:3 },
  title: { fontSize:20, fontWeight:'bold', marginBottom:12, textAlign:'center' },
  input: { borderWidth:1, borderColor:'#ccc', borderRadius:6, padding:8, marginBottom:12 },
  button: { backgroundColor:'#2ecc71', padding:12, borderRadius:6, alignItems:'center', marginBottom:8 },
  btnText: { color:'#fff', fontWeight:'bold' },
  link: { color:'#2980b9', textAlign:'center', marginTop:8 }
});
