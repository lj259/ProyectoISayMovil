import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Modal,
  TextInput,
  Alert,
  ScrollView,
} from "react-native";
import DateTimePicker from "@react-native-community/datetimepicker";
import { Picker } from "@react-native-picker/picker";

const API_URL = "http://192.168.100.44:8000";

export default function Transacciones() {
  const [transacciones, setTransacciones] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [monto, setMonto] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [fecha, setFecha] = useState(new Date());
  const [tipo, setTipo] = useState("egreso"); // egreso por defecto
  const [showDatePicker, setShowDatePicker] = useState(false);

  useEffect(() => {
    fetchTransacciones();
  }, []);

  const fetchTransacciones = async () => {
    try {
      const res = await fetch(`${API_URL}/transacciones`);
      const data = await res.json();
      setTransacciones(data);
    } catch (error) {
      console.error(error);
    }
  };

  const resetForm = () => {
    setMonto("");
    setDescripcion("");
    setFecha(new Date());
    setTipo("egreso");
    setEditingId(null);
  };

  const handleSave = async () => {
    if (!monto || !descripcion) {
      Alert.alert("Error", "Por favor completa todos los campos");
      return;
    }

    const nuevaTransaccion = {
      monto: parseFloat(monto),
      categoria: tipo, // ingreso / egreso / ahorro
      descripcion: descripcion,
      fecha: fecha.toISOString().split("T")[0], // YYYY-MM-DD
    };

    try {
      if (editingId) {
        // Editar
        await fetch(`${API_URL}/transacciones/${editingId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(nuevaTransaccion),
        });
        Alert.alert("Éxito", "Transacción actualizada correctamente");
      } else {
        // Crear
        await fetch(`${API_URL}/transacciones`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(nuevaTransaccion),
        });
        Alert.alert("Éxito", "Transacción creada correctamente");
      }
      fetchTransacciones();
      setModalVisible(false);
      resetForm();
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (id) => {
    Alert.alert("Confirmar", "¿Seguro que deseas eliminar esta transacción?", [
      { text: "Cancelar", style: "cancel" },
      {
        text: "Eliminar",
        style: "destructive",
        onPress: async () => {
          try {
            await fetch(`${API_URL}/transacciones/${id}`, { method: "DELETE" });
            fetchTransacciones();
          } catch (error) {
            console.error(error);
          }
        },
      },
    ]);
  };

  const openEdit = (item) => {
    setMonto(item.monto.toString());
    setDescripcion(item.descripcion);
    setTipo(item.tipo); // ingreso, egreso o ahorro
    setFecha(new Date(item.fecha));
    setEditingId(item.id);
    setModalVisible(true);
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={transacciones}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={styles.item}>
            <View>
              <Text style={styles.monto}>
                ${item.monto.toFixed(2)} - {item.categoria}
              </Text>
              <Text style={styles.descripcion}>{item.descripcion}</Text>
              <Text style={styles.fecha}>{item.fecha}</Text>
            </View>
            <View style={styles.buttons}>
              <TouchableOpacity onPress={() => openEdit(item)} style={styles.editButton}>
                <Text style={styles.buttonText}>Editar</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={() => handleDelete(item.id)} style={styles.deleteButton}>
                <Text style={styles.buttonText}>Eliminar</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      />

      <TouchableOpacity
        style={styles.addButton}
        onPress={() => {
          resetForm();
          setModalVisible(true);
        }}
      >
        <Text style={styles.addButtonText}>+ Agregar</Text>
      </TouchableOpacity>

      {/* Modal para agregar/editar */}
      <Modal visible={modalVisible} animationType="slide">
        <ScrollView style={styles.modalContainer}>
          <Text style={styles.modalTitle}>
            {editingId ? "Editar transacción" : "Nueva transacción"}
          </Text>

          <TextInput
            placeholder="Monto"
            keyboardType="numeric"
            value={monto}
            onChangeText={setMonto}
            style={styles.input}
          />

          <TextInput
            placeholder="Descripción"
            value={descripcion}
            onChangeText={setDescripcion}
            style={styles.input}
          />

          {/* Selector de tipo (Ingreso/Egreso/Ahorro) */}
          <Picker selectedValue={tipo} style={styles.input} onValueChange={setTipo}>
            <Picker.Item label="Gasto" value="egreso" />
            <Picker.Item label="Ingreso" value="ingreso" />
            <Picker.Item label="Ahorro" value="ahorro" />
          </Picker>

          {/* Fecha */}
          <TouchableOpacity
            onPress={() => setShowDatePicker(true)}
            style={styles.dateButton}
          >
            <Text>Seleccionar fecha: {fecha.toISOString().split("T")[0]}</Text>
          </TouchableOpacity>
          {showDatePicker && (
            <DateTimePicker
              value={fecha}
              mode="date"
              display="default"
              onChange={(event, selectedDate) => {
                setShowDatePicker(false);
                if (selectedDate) {
                  setFecha(selectedDate);
                }
              }}
            />
          )}

          <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
            <Text style={styles.saveButtonText}>
              {editingId ? "Actualizar" : "Guardar"}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.cancelButton}
            onPress={() => setModalVisible(false)}
          >
            <Text style={styles.cancelButtonText}>Cancelar</Text>
          </TouchableOpacity>
        </ScrollView>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#fff" },
  item: {
    backgroundColor: "#f5f5f5",
    padding: 15,
    marginVertical: 5,
    borderRadius: 8,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  monto: { fontSize: 16, fontWeight: "bold" },
  descripcion: { fontSize: 14, color: "#555" },
  fecha: { fontSize: 12, color: "#888" },
  buttons: { flexDirection: "row" },
  editButton: { backgroundColor: "#4caf50", padding: 8, borderRadius: 5, marginRight: 5 },
  deleteButton: { backgroundColor: "#e74c3c", padding: 8, borderRadius: 5 },
  buttonText: { color: "#fff", fontSize: 12 },
  addButton: {
    backgroundColor: "#2196f3",
    padding: 15,
    borderRadius: 50,
    alignItems: "center",
    marginTop: 10,
  },
  addButtonText: { color: "#fff", fontSize: 18 },
  modalContainer: { flex: 1, padding: 20, backgroundColor: "#fff" },
  modalTitle: { fontSize: 20, fontWeight: "bold", marginBottom: 20 },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 10,
    borderRadius: 8,
    marginBottom: 15,
  },
  dateButton: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 10,
    borderRadius: 8,
    marginBottom: 15,
    backgroundColor: "#f9f9f9",
  },
  saveButton: {
    backgroundColor: "#4caf50",
    padding: 15,
    borderRadius: 8,
    alignItems: "center",
    marginBottom: 10,
  },
  saveButtonText: { color: "#fff", fontSize: 16, fontWeight: "bold" },
  cancelButton: {
    backgroundColor: "#e74c3c",
    padding: 15,
    borderRadius: 8,
    alignItems: "center",
  },
  cancelButtonText: { color: "#fff", fontSize: 16, fontWeight: "bold" },
});
