import React, { useEffect, useState } from "react";
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity, Modal,
  TextInput, Alert, ActivityIndicator, ScrollView
} from "react-native";
import DateTimePicker from "@react-native-community/datetimepicker";
import { Picker } from "@react-native-picker/picker";

const API_URL = "http://192.168.100.44:8000";

const ajustarFecha = (date) => {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
};

export default function Transacciones() {
  const [transacciones, setTransacciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categorias, setCategorias] = useState([]);

  const [modalVisible, setModalVisible] = useState(false);
  const [monto, setMonto] = useState("");
  const [tipo, setTipo] = useState("");
  const [categoria, setCategoria] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [fecha, setFecha] = useState("");
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [date, setDate] = useState(new Date());

  const [modalEditarVisible, setModalEditarVisible] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editShowDatePicker, setEditShowDatePicker] = useState(false);
  const [editDate, setEditDate] = useState(new Date());

  const [modalEliminarVisible, setModalEliminarVisible] = useState(false);
  const [deleteId, setDeleteId] = useState(null);

  useEffect(() => {
    fetchTransacciones();
    fetchCategorias();
  }, []);

  const fetchCategorias = async () => {
    try {
      const res = await fetch(`${API_URL}/categorias`);
      const data = await res.json();
      setCategorias(data);
    } catch {
      Alert.alert("Error", "No se pudieron cargar las categorías");
    }
  };

  const fetchTransacciones = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/transacciones`);
      const data = await res.json();
      setTransacciones(data);
    } catch {
      Alert.alert("Error", "No se pudieron cargar las transacciones");
    } finally {
      setLoading(false);
    }
  };

  const crearTransaccion = async () => {
    if (!monto || !tipo || !categoria || !descripcion || !fecha) {
      Alert.alert("Error", "Todos los campos son obligatorios");
      return;
    }
    try {
      const res = await fetch(`${API_URL}/transacciones`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          monto: parseFloat(monto),
          tipo,
          categoria,
          descripcion,
          fecha,
        }),
      });
      if (!res.ok) throw new Error();
      setModalVisible(false);
      limpiarCampos();
      fetchTransacciones();
    } catch {
      Alert.alert("Error", "Error creando transacción");
    }
  };

  const abrirModalEditar = (item) => {
    setEditId(item.id);
    setMonto(String(item.monto));
    setTipo((item.tipo || "").toLowerCase());
    setCategoria(item.categoria || "");
    setDescripcion(item.descripcion || "");
    setFecha(item.fecha || "");
    setEditDate(item.fecha ? new Date(item.fecha) : new Date());
    setModalEditarVisible(true);
  };

  const editarTransaccion = async () => {
    if (!monto || !tipo || !categoria || !descripcion || !fecha) {
      Alert.alert("Error", "Todos los campos son obligatorios");
      return;
    }
    try {
      const res = await fetch(`${API_URL}/transacciones/${editId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          monto: parseFloat(monto),
          tipo,
          categoria,
          descripcion,
          fecha,
        }),
      });
      if (!res.ok) throw new Error();
      setModalEditarVisible(false);
      limpiarCampos();
      fetchTransacciones();
    } catch {
      Alert.alert("Error", "Error editando transacción");
    }
  };

  const abrirModalEliminar = (id) => {
    setDeleteId(id);
    setModalEliminarVisible(true);
  };

  const eliminarTransaccion = async () => {
    try {
      const res = await fetch(`${API_URL}/transacciones/${deleteId}`, { method: "DELETE" });
      if (!res.ok) throw new Error();
      setModalEliminarVisible(false);
      fetchTransacciones();
    } catch {
      Alert.alert("Error", "Error eliminando transacción");
    }
  };

  const limpiarCampos = () => {
    setMonto(""); setTipo(""); setCategoria("");
    setDescripcion(""); setFecha("");
    setDate(new Date()); setEditDate(new Date());
  };

  const onChangeDate = (_, selectedDate) => {
    setShowDatePicker(false);
    if (selectedDate) {
      setDate(selectedDate);
      setFecha(ajustarFecha(selectedDate));
    }
  };

  const onChangeEditDate = (_, selectedDate) => {
    setEditShowDatePicker(false);
    if (selectedDate) {
      setEditDate(selectedDate);
      setFecha(ajustarFecha(selectedDate));
    }
  };

  const renderCardItem = ({ item }) => {
    const t = (item.tipo || "").toLowerCase();
    const cardBackground = t === "ingreso" ? "#d4edda" : t === "egreso" ? "#f8d7da" : "#fff3cd";
    return (
      <View style={[styles.card, { backgroundColor: cardBackground }]}>
        <View style={styles.cardRow}><Text style={styles.cardLabel}>Monto:</Text><Text style={styles.cardValue}>${item.monto}</Text></View>
        <View style={styles.cardRow}><Text style={styles.cardLabel}>Tipo:</Text><Text style={styles.cardValue}>{item.tipo?.charAt(0).toUpperCase() + item.tipo?.slice(1)}</Text></View>
        <View style={styles.cardRow}><Text style={styles.cardLabel}>Categoría:</Text><Text style={styles.cardValue}>{item.categoria}</Text></View>
        <View style={styles.cardRow}><Text style={styles.cardLabel}>Descripción:</Text><Text style={styles.cardValue}>{item.descripcion}</Text></View>
        <View style={styles.cardRow}><Text style={styles.cardLabel}>Fecha:</Text><Text style={styles.cardValue}>{item.fecha}</Text></View>
        <View style={styles.cardActions}>
          <TouchableOpacity onPress={() => abrirModalEditar(item)}><Text style={styles.editText}>✏</Text></TouchableOpacity>
          <TouchableOpacity onPress={() => abrirModalEliminar(item.id)}><Text style={styles.deleteText}>🗑</Text></TouchableOpacity>
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Registro de Transacciones</Text>

      {loading ? (
        <ActivityIndicator size="large" color="#007bff" />
      ) : (
        <FlatList
          data={transacciones}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderCardItem}
          contentContainerStyle={{ paddingBottom: 80 }}
        />
      )}

      <TouchableOpacity style={styles.fab} onPress={() => setModalVisible(true)}>
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>

      {/* Crear */}
      <Modal visible={modalVisible} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={{ paddingBottom: 10 }}>
              <Text style={styles.modalTitle}>Nueva Transacción</Text>

              <Text style={styles.label}>Monto</Text>
              <TextInput style={styles.input} placeholder="Monto" keyboardType="numeric" value={monto} onChangeText={setMonto} />

              <Text style={styles.label}>Tipo</Text>
              <Picker
                selectedValue={tipo}
                onValueChange={(v) => { setTipo(v); setCategoria(""); }}
                style={{ marginBottom: 10 }}
                itemStyle={{ color: "#000" }}
                dropdownIconColor="#000"
              >
                <Picker.Item label="Selecciona el tipo" value="" color="#888" />
                <Picker.Item label="Ingreso" value="ingreso" color="#000" />
                <Picker.Item label="Egreso" value="egreso" color="#000" />
              </Picker>

              <Text style={styles.label}>Categoría</Text>
              <Picker
                selectedValue={categoria}
                onValueChange={setCategoria}
                style={{ marginBottom: 10 }}
                itemStyle={{ color: "#000" }}
                dropdownIconColor="#000"
              >
                <Picker.Item label="Selecciona la categoría" value="" color="#888" />
                {categorias
                  .filter((c) => c.tipo?.toLowerCase().trim() === tipo?.toLowerCase().trim())
                  .map((c) => (
                    <Picker.Item key={c.id} label={c.nombre} value={c.nombre} color="#000" />
                  ))}
              </Picker>

              <Text style={styles.label}>Descripción</Text>
              <TextInput style={styles.input} placeholder="Descripción" value={descripcion} onChangeText={setDescripcion} />

              <Text style={styles.label}>Fecha</Text>
              <TouchableOpacity style={styles.input} onPress={() => setShowDatePicker(true)}>
                <Text>{fecha ? fecha : "Selecciona una fecha"}</Text>
              </TouchableOpacity>
              {showDatePicker && (
                <DateTimePicker value={date} mode="date" display="default" onChange={onChangeDate} />
              )}

              <View style={styles.buttonRow}>
                <TouchableOpacity style={styles.addButton} onPress={crearTransaccion}><Text style={styles.addButtonText}>Agregar</Text></TouchableOpacity>
                <TouchableOpacity style={styles.cancelButton} onPress={() => setModalVisible(false)}><Text style={styles.cancelButtonText}>Cancelar</Text></TouchableOpacity>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* Editar */}
      <Modal visible={modalEditarVisible} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={{ paddingBottom: 10 }}>
              <Text style={styles.modalTitle}>Editar Transacción</Text>

              <Text style={styles.label}>Monto</Text>
              <TextInput style={styles.input} placeholder="Monto" keyboardType="numeric" value={monto} onChangeText={setMonto} />

              <Text style={styles.label}>Tipo</Text>
              <Picker
                selectedValue={tipo}
                onValueChange={(v) => { setTipo(v); setCategoria(""); }}
                style={{ marginBottom: 10 }}
                itemStyle={{ color: "#000" }}
                dropdownIconColor="#000"
              >
                <Picker.Item label="Selecciona el tipo" value="" color="#888" />
                <Picker.Item label="Ingreso" value="ingreso" color="#000" />
                <Picker.Item label="Egreso" value="egreso" color="#000" />
              </Picker>

              <Text style={styles.label}>Categoría</Text>
              <Picker
                selectedValue={categoria}
                onValueChange={setCategoria}
                style={{ marginBottom: 10 }}
                itemStyle={{ color: "#000" }}
                dropdownIconColor="#000"
              >
                <Picker.Item label="Selecciona la categoría" value="" color="#888" />
                {categorias
                  .filter((c) => c.tipo?.toLowerCase().trim() === tipo?.toLowerCase().trim())
                  .map((c) => (
                    <Picker.Item key={c.id} label={c.nombre} value={c.nombre} color="#000" />
                  ))}
              </Picker>

              <Text style={styles.label}>Descripción</Text>
              <TextInput style={styles.input} placeholder="Descripción" value={descripcion} onChangeText={setDescripcion} />

              <Text style={styles.label}>Fecha</Text>
              <TouchableOpacity style={styles.input} onPress={() => setEditShowDatePicker(true)}>
                <Text>{fecha ? fecha : "Selecciona una fecha"}</Text>
              </TouchableOpacity>
              {editShowDatePicker && (
                <DateTimePicker value={editDate} mode="date" display="default" onChange={onChangeEditDate} />
              )}

              <View style={styles.buttonRow}>
                <TouchableOpacity style={styles.addButton} onPress={editarTransaccion}><Text style={styles.addButtonText}>Guardar</Text></TouchableOpacity>
                <TouchableOpacity style={styles.cancelButton} onPress={() => setModalEditarVisible(false)}><Text style={styles.cancelButtonText}>Cancelar</Text></TouchableOpacity>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* Eliminar */}
      <Modal visible={modalEliminarVisible} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            <Text style={styles.modalTitle}>¿Eliminar transacción?</Text>
            <View style={styles.buttonRow}>
              <TouchableOpacity style={styles.addButton} onPress={eliminarTransaccion}><Text style={styles.addButtonText}>Eliminar</Text></TouchableOpacity>
              <TouchableOpacity style={styles.cancelButton} onPress={() => setModalEliminarVisible(false)}><Text style={styles.cancelButtonText}>Cancelar</Text></TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fff" },
  title: { fontSize: 18, fontWeight: "bold", marginBottom: 10, textAlign: "center" },
  fab: { position: "absolute", bottom: 20, right: 20, backgroundColor: "#007bff", width: 50, height: 50, borderRadius: 25, justifyContent: "center", alignItems: "center", elevation: 5 },
  fabText: { color: "#fff", fontSize: 24, fontWeight: "bold" },
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "center", alignItems: "center" },
  modalContainer: { width: "85%", backgroundColor: "#fff", borderRadius: 15, padding: 20 },
  modalTitle: { fontSize: 18, fontWeight: "bold", marginBottom: 15, textAlign: "center" },
  label: { fontSize: 14, fontWeight: "bold", marginBottom: 4, marginTop: 8 },
  input: { borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 10, marginBottom: 10 },
  buttonRow: { flexDirection: "row", justifyContent: "space-around", marginTop: 10 },
  addButton: { backgroundColor: "#007bff", paddingVertical: 10, paddingHorizontal: 20, borderRadius: 8 },
  addButtonText: { color: "#fff", fontWeight: "bold" },
  cancelButton: { paddingVertical: 10, paddingHorizontal: 20 },
  cancelButtonText: { color: "#007bff", fontWeight: "bold" },
  editText: { marginRight: 15, fontSize: 18 },
  deleteText: { fontSize: 18 },
  card: { borderRadius: 10, padding: 15, marginBottom: 12, elevation: 2, shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 3 },
  cardRow: { flexDirection: "row", justifyContent: "space-between", marginBottom: 4 },
  cardLabel: { fontWeight: "bold", color: "#333" },
  cardValue: { color: "#212529" },
  cardActions: { flexDirection: "row", justifyContent: "flex-end", marginTop: 10 },
});