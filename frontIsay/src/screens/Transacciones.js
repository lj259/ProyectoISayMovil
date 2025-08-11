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
  ActivityIndicator,
  ScrollView
} from "react-native";
import DateTimePicker from "@react-native-community/datetimepicker";
import { getTransacciones, crearTransaccion as crearTransaccionAPI, editarTransaccion as editarTransaccionAPI, eliminarTransaccion as  eliminarTransaccionAPI} from "../utils/api";

// Función para formatear fecha local y evitar que se sume un día
const ajustarFecha = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

export default function Transacciones() {
  const [transacciones, setTransacciones] = useState([]);
  const [loading, setLoading] = useState(true);

  // Estados para modal Crear
  const [modalVisible, setModalVisible] = useState(false);
  const [monto, setMonto] = useState("");
  const [tipo, setTipo] = useState(""); // ingreso, egreso o ahorro
  const [descripcion, setDescripcion] = useState("");
  const [fecha, setFecha] = useState("");
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [date, setDate] = useState(new Date());

  // Estados para modal Editar
  const [modalEditarVisible, setModalEditarVisible] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editShowDatePicker, setEditShowDatePicker] = useState(false);
  const [editDate, setEditDate] = useState(new Date());

  // Estados para modal Eliminar
  const [modalEliminarVisible, setModalEliminarVisible] = useState(false);
  const [deleteId, setDeleteId] = useState(null);

  useEffect(() => {
    fetchTransacciones();
  }, []);

  // Obtener transacciones
  const fetchTransacciones = async () => {
    try {
      setLoading(true);
      const data = await getTransacciones();
      setTransacciones(data);
    } catch (error) {
      console.log("Error cargando transacciones", error);
      Alert.alert("Error", "No se pudieron cargar las transacciones");
    } finally {
      setLoading(false);
    }
  };

  // Crear transacción
  const crearTransaccion = async () => {
    if (!monto || !tipo || !descripcion || !fecha) {
      Alert.alert("Error", "Todos los campos son obligatorios");
      return;
    }

    try {
      const res = await crearTransaccionAPI({
        monto: parseFloat(monto),
        tipo,
        descripcion,
        fecha
      });
      setTransacciones([...transacciones, res]);
      setModalVisible(false);
      limpiarCampos();
      fetchTransacciones();
    } catch (error) {
      console.log("Error creando transacción", error);
    }
  };

  // Editar transacción
  const abrirModalEditar = (item) => {
    setEditId(item.id);
    setMonto(String(item.monto));
    setTipo(item.tipo.toLowerCase());
    setDescripcion(item.descripcion);
    setFecha(item.fecha);
    setEditDate(new Date(item.fecha));
    setModalEditarVisible(true);
  };

const editarTransaccion = async () => {
  if (!monto || !tipo || !descripcion || !fecha) {
    Alert.alert("Error", "Todos los campos son obligatorios");
    return;
  }

  try {
    await editarTransaccionAPI(editId, {
      monto: parseFloat(monto),
      tipo,
      descripcion,
      fecha
    });

    setModalEditarVisible(false);
    limpiarCampos();
    fetchTransacciones();
  } catch (error) {
    console.log("Error editando transacción", error);
    Alert.alert("Error", "No se pudo editar la transacción");
  }
};


  // Eliminar transacción
  const abrirModalEliminar = (id) => {
    setDeleteId(id);
    setModalEliminarVisible(true);
  };

const eliminarTransaccion = async () => {
  try {
    await eliminarTransaccionAPI(deleteId);
    setModalEliminarVisible(false);
    fetchTransacciones();
  } catch (error) {
    console.log("Error eliminando transacción", error);
    Alert.alert("Error", "No se pudo eliminar la transacción");
  }
};


  // Limpiar campos
  const limpiarCampos = () => {
    setMonto("");
    setTipo("");
    setDescripcion("");
    setFecha("");
    setDate(new Date());
    setEditDate(new Date());
  };

  // Render de cada transacción en tabla
  const renderTableHeader = () => (
    <View style={styles.tableRowHeader}>
      <Text style={[styles.tableCell, styles.headerCell]}>Monto</Text>
      <Text style={[styles.tableCell, styles.headerCell]}>Tipo</Text>
      <Text style={[styles.tableCell, styles.headerCell]}>Descripción</Text>
      <Text style={[styles.tableCell, styles.headerCell]}>Fecha</Text>
      <Text style={[styles.tableCell, styles.headerCell]}>Acciones</Text>
    </View>
  );

  const renderTableRow = ({ item }) => (
    <View style={styles.tableRow}>
      <Text style={styles.tableCell}>{item.monto}</Text>
      <Text style={styles.tableCell}>{item.tipo.charAt(0).toUpperCase() + item.tipo.slice(1)}</Text>
      <Text style={styles.tableCell}>{item.descripcion}</Text>
      <Text style={styles.tableCell}>{item.fecha}</Text>
      <View style={[styles.tableCell, styles.actionCell]}>
        <TouchableOpacity onPress={() => abrirModalEditar(item)}>
          <Text style={styles.editText}>✏️</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => abrirModalEliminar(item.id)}>
          <Text style={styles.deleteText}>🗑️</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  // DatePicker para crear
  const onChangeDate = (event, selectedDate) => {
    setShowDatePicker(false);
    if (selectedDate) {
      setDate(selectedDate);
      setFecha(ajustarFecha(selectedDate));
    }
  };

  // DatePicker para editar
  const onChangeEditDate = (event, selectedDate) => {
    setEditShowDatePicker(false);
    if (selectedDate) {
      setEditDate(selectedDate);
      setFecha(ajustarFecha(selectedDate));
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Registro de Transacciones</Text>

      {loading ? (
        <ActivityIndicator size="large" color="#007bff" />
      ) : (
        <ScrollView horizontal>
          <View style={styles.table}>
            {renderTableHeader()}
            <FlatList
              data={transacciones}
              keyExtractor={(item) => item.id.toString()}
              renderItem={renderTableRow}
            />
          </View>
        </ScrollView>
      )}

      {/* Botón flotante agregar */}
      <TouchableOpacity
        style={styles.fab}
        onPress={() => setModalVisible(true)}
      >
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>

      {/* MODALES */}
      {/* Crear */}
      <Modal visible={modalVisible} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            <Text style={styles.modalTitle}>Nueva Transacción</Text>
            <Text style={styles.label}>Monto</Text>
            <TextInput
              style={styles.input}
              placeholder="Monto"
              keyboardType="numeric"
              value={monto}
              onChangeText={setMonto}
            />
            <Text style={styles.label}>Tipo</Text>
            <View style={styles.typeSelector}>
              <TouchableOpacity
                style={[
                  styles.typeButton,
                  tipo === "ingreso" && styles.typeButtonSelectedIngreso
                ]}
                onPress={() => setTipo("ingreso")}
              >
                <Text style={[
                  styles.typeButtonText,
                  tipo === "ingreso" && styles.typeButtonTextSelected
                ]}>
                  Ingreso
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.typeButton,
                  tipo === "egreso" && styles.typeButtonSelectedEgreso
                ]}
                onPress={() => setTipo("egreso")}
              >
                <Text style={[
                  styles.typeButtonText,
                  tipo === "egreso" && styles.typeButtonTextSelected
                ]}>
                  Egreso
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.typeButton,
                  tipo === "ahorro" && { backgroundColor: "#ffc107", borderColor: "#ffc107" }
                ]}
                onPress={() => setTipo("ahorro")}
              >
                <Text style={[
                  styles.typeButtonText,
                  tipo === "ahorro" && { color: "#fff" }
                ]}>
                  Ahorro
                </Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.label}>Descripción</Text>
            <TextInput
              style={styles.input}
              placeholder="Descripción"
              value={descripcion}
              onChangeText={setDescripcion}
            />
            <Text style={styles.label}>Fecha</Text>
            <TouchableOpacity
              style={styles.input}
              onPress={() => setShowDatePicker(true)}
            >
              <Text>{fecha ? fecha : "Selecciona una fecha"}</Text>
            </TouchableOpacity>
            {showDatePicker && (
              <DateTimePicker
                value={date}
                mode="date"
                display="default"
                onChange={onChangeDate}
              />
            )}
            <View style={styles.buttonRow}>
              <TouchableOpacity style={styles.addButton} onPress={crearTransaccion}>
                <Text style={styles.addButtonText}>Agregar</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.cancelButtonText}>Cancelar</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Editar */}
      <Modal visible={modalEditarVisible} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            <Text style={styles.modalTitle}>Editar Transacción</Text>
            <Text style={styles.label}>Monto</Text>
            <TextInput
              style={styles.input}
              placeholder="Monto"
              keyboardType="numeric"
              value={monto}
              onChangeText={setMonto}
            />
            <Text style={styles.label}>Tipo</Text>
            <View style={styles.typeSelector}>
              <TouchableOpacity
                style={[
                  styles.typeButton,
                  tipo === "ingreso" && styles.typeButtonSelectedIngreso
                ]}
                onPress={() => setTipo("ingreso")}
              >
                <Text style={[
                  styles.typeButtonText,
                  tipo === "ingreso" && styles.typeButtonTextSelected
                ]}>
                  Ingreso
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.typeButton,
                  tipo === "egreso" && styles.typeButtonSelectedEgreso
                ]}
                onPress={() => setTipo("egreso")}
              >
                <Text style={[
                  styles.typeButtonText,
                  tipo === "egreso" && styles.typeButtonTextSelected
                ]}>
                  Egreso
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.typeButton,
                  tipo === "ahorro" && { backgroundColor: "#ffc107", borderColor: "#ffc107" }
                ]}
                onPress={() => setTipo("ahorro")}
              >
                <Text style={[
                  styles.typeButtonText,
                  tipo === "ahorro" && { color: "#fff" }
                ]}>
                  Ahorro
                </Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.label}>Descripción</Text>
            <TextInput
              style={styles.input}
              placeholder="Descripción"
              value={descripcion}
              onChangeText={setDescripcion}
            />
            <Text style={styles.label}>Fecha</Text>
            <TouchableOpacity
              style={styles.input}
              onPress={() => setEditShowDatePicker(true)}
            >
              <Text>{fecha ? fecha : "Selecciona una fecha"}</Text>
            </TouchableOpacity>
            {editShowDatePicker && (
              <DateTimePicker
                value={editDate}
                mode="date"
                display="default"
                onChange={onChangeEditDate}
              />
            )}
            <View style={styles.buttonRow}>
              <TouchableOpacity style={styles.addButton} onPress={editarTransaccion}>
                <Text style={styles.addButtonText}>Guardar</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setModalEditarVisible(false)}
              >
                <Text style={styles.cancelButtonText}>Cancelar</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Eliminar */}
      <Modal visible={modalEliminarVisible} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            <Text style={styles.modalTitle}>¿Eliminar transacción?</Text>
            <View style={styles.buttonRow}>
              <TouchableOpacity style={styles.addButton} onPress={eliminarTransaccion}>
                <Text style={styles.addButtonText}>Eliminar</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setModalEliminarVisible(false)}
              >
                <Text style={styles.cancelButtonText}>Cancelar</Text>
              </TouchableOpacity>
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

  // Tabla
  table: { minWidth: 600 },
  tableRowHeader: {
    flexDirection: "row",
    backgroundColor: "#007bff",
    paddingVertical: 8,
    borderRadius: 8,
    marginBottom: 2,
  },
  tableRow: {
    flexDirection: "row",
    backgroundColor: "#f9f9f9",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
    alignItems: "center",
  },
  tableCell: {
    flex: 1,
    textAlign: "center",
    fontSize: 14,
    paddingHorizontal: 4,
  },
  headerCell: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 15,
  },
  actionCell: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
  },

  // Botón flotante
  fab: {
    position: "absolute",
    bottom: 20,
    right: 20,
    backgroundColor: "#007bff",
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: "center",
    alignItems: "center",
    elevation: 5,
  },
  fabText: { color: "#fff", fontSize: 24, fontWeight: "bold" },

  // Modal
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "center",
    alignItems: "center",
  },
  modalContainer: {
    width: "85%",
    backgroundColor: "#fff",
    borderRadius: 15,
    padding: 20,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 15,
    textAlign: "center",
  },
  label: {
    fontSize: 14,
    fontWeight: "bold",
    marginBottom: 4,
    marginTop: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 8,
    padding: 10,
    marginBottom: 10,
  },
  typeSelector: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 10,
  },
  typeButton: {
    flex: 1,
    padding: 12,
    marginHorizontal: 5,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#ccc",
    alignItems: "center",
  },
  typeButtonSelectedIngreso: {
    backgroundColor: "#28a745",
    borderColor: "#28a745",
  },
  typeButtonSelectedEgreso: {
    backgroundColor: "#dc3545",
    borderColor: "#dc3545",
  },
  typeButtonText: { color: "#000", fontWeight: "600" },
  typeButtonTextSelected: { color: "#fff" },
  buttonRow: {
    flexDirection: "row",
    justifyContent: "space-around",
    marginTop: 10,
  },
  addButton: {
    backgroundColor: "#007bff",
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  addButtonText: { color: "#fff", fontWeight: "bold" },
  cancelButton: { paddingVertical: 10, paddingHorizontal: 20 },
  cancelButtonText: { color: "#007bff", fontWeight: "bold" },
  editText: { marginRight: 15, fontSize: 18 }, 
  deleteText: {fontSize: 18}, 
});