import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert
} from 'react-native';

const API_URL = "http://192.168.1.65:8000";

export default function EditarPerfil({ navigation }) {
  const [usuario, setUsuario] = useState({
    nombre_usuario: '',
    correo: '',
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
        nombre_usuario: data.nombre_usuario,
        correo: data.correo,
        telefono: data.telefono
      });
    } catch (error) {
      console.log('Error al cargar perfil', error);
      Alert.alert('Error', 'No se pudo cargar tu perfil');
    }
  };

  const guardarCambios = async () => {
    try {
      const res = await fetch(`${API_URL}/usuarios/1`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(usuario)
      });
      if (!res.ok) throw new Error('Error al actualizar');
      Alert.alert('Perfil actualizado', 'Los cambios fueron guardados', [
        { text: 'OK', onPress: () => navigation.goBack() }
      ]);
    } catch (error) {
      console.log('Error al guardar cambios', error);
      Alert.alert('Error', 'No se pudo guardar tu perfil');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.form}>
        <Text style={styles.label}>Nombre completo</Text>
        <TextInput
          style={styles.input}
          value={usuario.nombre_usuario}
          onChangeText={(text) => setUsuario({ ...usuario, nombre_usuario: text })}
        />

        <Text style={styles.label}>Correo electrónico</Text>
        <TextInput
          style={styles.input}
          value={usuario.correo}
          keyboardType="email-address"
          onChangeText={(text) => setUsuario({ ...usuario, correo: text })}
        />

        <Text style={styles.label}>Teléfono</Text>
        <TextInput
          style={styles.input}
          value={usuario.telefono}
          keyboardType="phone-pad"
          onChangeText={(text) => setUsuario({ ...usuario, telefono: text })}
        />

        <TouchableOpacity style={styles.button} onPress={guardarCambios}>
          <Text style={styles.buttonText}>Guardar Cambios</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.button, { backgroundColor: '#ccc' }]} onPress={() => navigation.goBack()}>
          <Text style={[styles.buttonText, { color: '#000' }]}>Cancelar</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  form: { padding: 16 },
  label: { fontSize: 14, fontWeight: '600', marginTop: 12 },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    padding: 8,
    marginTop: 4
  },
  button: {
    backgroundColor: '#2ecc71',
    padding: 12,
    borderRadius: 6,
    marginTop: 24,
    alignItems: 'center'
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold'
  }
});
