import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from "react-native";

const API_URL = "http://192.168.100.44:8000"; 

export default function Transacciones() {
  const [transacciones, setTransacciones] = useState([]);

  useEffect(() => {
    fetchTransacciones();
  }, []);

  const fetchTransacciones = async () => {
    try {
      const res = await fetch(`${API_URL}/transacciones`);
      const data = await res.json();
      setTransacciones(data);
    } catch (error) {
      console.log("Error cargando transacciones:", error);
    }
  };

  const renderItem = ({ item }) => (
    <View style={[styles.card, item.tipo === "ingreso" ? styles.ingreso : item.tipo === "egreso" ? styles.egreso : styles.ahorro]}>
      <View style={styles.row}>
        <Text style={styles.monto}>${item.monto.toFixed(2)}</Text>
        <Text style={styles.fecha}>{new Date(item.fecha).toLocaleDateString()}</Text>
      </View>
      <Text style={styles.categoria}>{item.categoria}</Text>
      <Text style={styles.descripcion}>{item.descripcion}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={transacciones}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderItem}
        ListEmptyComponent={<Text style={styles.empty}>No hay transacciones registradas</Text>}
      />

      {/* Botón flotante para agregar */}
      <TouchableOpacity style={styles.fab} onPress={() => alert("Formulario para agregar transacción")}>
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: "#fff",
  },
  card: {
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    elevation: 2,
  },
  ingreso: { backgroundColor: "#d4edda" }, // verde claro
  egreso: { backgroundColor: "#f8d7da" },  // rojo claro
  ahorro: { backgroundColor: "#d1ecf1" },  // azul claro
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  monto: { fontSize: 18, fontWeight: "bold" },
  fecha: { fontSize: 14, color: "#555" },
  categoria: { fontSize: 16, color: "#333", marginTop: 4 },
  descripcion: { fontSize: 14, color: "#666" },
  empty: { textAlign: "center", marginTop: 20, color: "#999" },
  fab: {
    position: "absolute",
    right: 20,
    bottom: 20,
    backgroundColor: "#007bff",
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: "center",
    alignItems: "center",
    elevation: 5,
  },
  fabText: { fontSize: 28, color: "#fff" },
});