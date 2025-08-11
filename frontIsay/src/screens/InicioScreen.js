import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

export default function InicioScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <Text style={styles.logo}>LanaApp</Text>
      <Text style={styles.bienvenido}>BIENVENIDO</Text>
      <TouchableOpacity onPress={() => navigation.navigate('Login')}>
        <Text style={styles.triangulo}>▲</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#fff' },
  logo: { fontSize: 34, fontWeight: 'bold', color: '#2e7d32', marginBottom: 8 },
  bienvenido: { fontSize: 20, marginBottom: 20 },
  triangulo: { fontSize: 30, color: '#2e7d32' }
});
