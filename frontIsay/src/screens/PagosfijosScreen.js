import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Modal,
  TextInput,
  Switch,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import DateTimePicker from '@react-native-community/datetimepicker';
import { Picker } from '@react-native-picker/picker';
import { fetchCategorias } from "../utils/api";
import { crearPagoFijo } from "../utils/api";
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function PagosFijosScreen() {
  const [modalAdd, setModalAdd] = useState(false);
  const [modalEdit, setModalEdit] = useState(false);
  const [modalDelete, setModalDelete] = useState(false);
  
  const [fechaVencimiento, setFechaVencimiento] = useState(new Date());
  const [mostrarFechaPicker, setMostrarFechaPicker] = useState(false);

  const [categorias, setCategorias] = useState([]);
  const [nombrePago, setNombrePago] = useState("");
  const [monto, setMonto] = useState("");

  const [selectedCategory, setSelectedCategory] = useState('');

  const handleGuardarPago = async () => {
    const usuario_id = parseInt(await AsyncStorage.getItem('usuario_id'));
    const nuevoPago = {
      descripcion: nombrePago,
      usuario_id: usuario_id,
      categoria_id: selectedCategory,
      monto: parseFloat(monto),
      fecha: fechaVencimiento.toISOString().split("T")[0]
    };

    try {
      console.log("Guardando pago fijo:", nuevoPago);
      const response = await crearPagoFijo(nuevoPago);
      console.log("Respuesta del servidor:", response);
      setModalAdd(false);
      // Aquí podrías recargar la lista de pagos o mostrar un mensaje
    } catch (err) {
      console.error("Error al guardar pago:", err);
    }
  };
  const onSelect = (value) => {
    setSelectedCategory(value);
  };

  useEffect(() => {
    const loadCategorias = async () => {
      try {
        const data = await fetchCategorias();
        setCategorias(data);
      } catch (err) {
        console.error("Error al cargar categorías:", err);
      }
    };
    loadCategorias();
  }, []);

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <Text style={styles.title}>
        <Text style={styles.titleGreen}>Lana</Text> App
      </Text>


      {/* Section Title */}
      <View style={styles.headerRow}>
        <Text style={styles.sectionTitle}>Pagos Fijos</Text>
        <TouchableOpacity style={styles.addButton} onPress={() => setModalAdd(true)}>
          <Ionicons name="add" size={20} color="#fff" />
          <Text style={styles.addButtonText}>Nuevo Pago Fijo</Text>
        </TouchableOpacity>
      </View>

      {/* Alert */}
      <View style={styles.alertBox}>
        <Ionicons name="warning" size={20} color="#a94442" style={{ marginRight: 5 }} />
        <Text style={styles.alertText}>
          <Text style={{ fontWeight: "bold" }}>Alerta de Presupuesto:</Text> Tu balance actual ($1850) es insuficiente para cubrir todos los pagos fijos mensuales ($21.250). Faltan $19.400.
        </Text>
      </View>

      {/* Cards */}
      <View style={styles.card}>
        <Text style={styles.cardLabel}>Pagos programados</Text>
        <Text style={styles.cardNumberBlue}>2</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardLabel}>Total mensual</Text>
        <Text style={styles.cardNumberRed}>$21.250</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardLabel}>Balance Disponible</Text>
        <Text style={styles.cardNumberGreen}>$1850</Text>
      </View>

      {/* Table */}
      <View style={styles.tableContainer}>
        <Text style={styles.tableTitle}>Pagos Programados</Text>
        <Text style={styles.tableSubtitle}>
          Gestiona tus pagos recurrentes y automáticos
        </Text>

        <View style={styles.tableHeader}>
          {["Nombre", "Categoría", "Monto", "Vencimiento", "Estado", "Frecuencia", "Acciones"].map((header, i) => (
            <Text key={i} style={styles.tableHeaderText}>{header}</Text>
          ))}
        </View>

        <View style={styles.tableRow}>
          <Text style={styles.tableCell}>Renta</Text>
          <Text style={styles.tableCell}>Vivienda</Text>
          <Text style={styles.tableCell}>$1200</Text>
          <Text style={styles.tableCell}>31/1/2024</Text>
          <Text style={styles.statusVencido}>Vencido</Text>
          <Text style={styles.tableCell}>Mensual</Text>
          <View style={{ flexDirection: "row", gap: 8 }}>
            <TouchableOpacity onPress={() => setModalEdit(true)}>
              <Ionicons name="create-outline" size={18} color="black" />
            </TouchableOpacity>
            <TouchableOpacity onPress={() => setModalDelete(true)}>
              <Ionicons name="trash-outline" size={18} color="black" />
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {/* MODAL AGREGAR */}
      <Modal visible={modalAdd} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalBox}>
            <Text style={styles.modalTitle}>Agrega un nuevo Pago Fijo</Text>
            <TextInput placeholder="Nombre del Pago" style={styles.input} onChangeText={setNombrePago} />
            <TextInput placeholder="Monto" style={styles.input} keyboardType="numeric" onChangeText={setMonto} />
            <View style={styles.input}>
              <Picker
                selectedValue={selectedCategory}
                onValueChange={onSelect}
              >
                <Picker.Item label="Selecciona una categoría" value="" />
                {categorias.map((cat) => (
                  <Picker.Item key={cat.id} label={cat.nombre} value={cat.id} />
                ))}
              </Picker>
            </View>

            <TouchableOpacity onPress={() => setMostrarFechaPicker(true)} style={styles.input}>
              <Text>{fechaVencimiento.toLocaleDateString()}</Text>
            </TouchableOpacity>

            {mostrarFechaPicker && (
              <DateTimePicker
                value={fechaVencimiento}
                mode="date"
                display="default"
                onChange={(event, selectedDate) => {
                  setMostrarFechaPicker(false);
                  if (selectedDate) setFechaVencimiento(selectedDate);
                }}
              />
            )}
            
            <TouchableOpacity style={styles.primaryBtn} onPress={handleGuardarPago}>
              <Text style={styles.primaryBtnText}>Guardar pago</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.cancelBtn} onPress={() => setModalAdd(false)}>
              <Text>Cancelar</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* MODAL EDITAR */}
      <Modal visible={modalEdit} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalBox}>
            <Text style={styles.modalTitle}>Editar Pago Fijo</Text>
            <TextInput placeholder="Nombre del Pago" style={styles.input} />
            <TextInput placeholder="Monto" style={styles.input} keyboardType="numeric" />
            <View style={styles.input}>
              <Picker
                selectedValue={selectedCategory}
                onValueChange={onSelect}
              >
                <Picker.Item label="Selecciona una categoría" value="" />
                {categorias.map((cat) => (
                  <Picker.Item key={cat.id} label={cat.nombre} value={cat.id} />
                ))}
              </Picker>
            </View>

            <TouchableOpacity onPress={() => setMostrarFechaPicker(true)} style={styles.input}>
              <Text>{fechaVencimiento.toLocaleDateString()}</Text>
            </TouchableOpacity>

            {mostrarFechaPicker && (
              <DateTimePicker
                value={fechaVencimiento}
                mode="date"
                display="default"
                onChange={(event, selectedDate) => {
                  setMostrarFechaPicker(false);
                  if (selectedDate) setFechaVencimiento(selectedDate);
                }}
              />
            )}

            <TextInput placeholder="Frecuencia" style={styles.input} />
            <TouchableOpacity style={styles.primaryBtnBlack} onPress={() => setModalEdit(false)}>
              <Text style={styles.primaryBtnText}>Actualizar pago</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.cancelBtn} onPress={() => setModalEdit(false)}>
              <Text>Cancelar</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* MODAL ELIMINAR */}
      <Modal visible={modalDelete} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalBox}>
            <Text style={styles.modalTitle}>¿Eliminar Pago programado?</Text>
            <TouchableOpacity style={styles.primaryBtnBlack} onPress={() => setModalDelete(false)}>
              <Text style={styles.primaryBtnText}>Eliminar</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.cancelBtn} onPress={() => setModalDelete(false)}>
              <Text>Cancelar</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff", padding: 16 },
  title: { fontSize: 28, fontWeight: "bold", marginBottom: 10 },
  titleGreen: { color: "#6ab04c" },
  tabs: { flexDirection: "row", marginBottom: 15, flexWrap: "wrap" },
  tabText: { marginRight: 15, fontSize: 14, color: "#555" },
  activeTab: { fontWeight: "bold", color: "#000" },
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 10 },
  sectionTitle: { fontSize: 20, fontWeight: "bold" },
  addButton: { flexDirection: "row", alignItems: "center", backgroundColor: "#2f3640", paddingHorizontal: 10, paddingVertical: 6, borderRadius: 5 },
  addButtonText: { color: "#fff", marginLeft: 5, fontSize: 14 },
  alertBox: { flexDirection: "row", backgroundColor: "#f2dede", borderWidth: 1, borderColor: "#ebccd1", padding: 10, borderRadius: 5, marginBottom: 15 },
  alertText: { fontSize: 13, color: "#a94442", flex: 1 },
  card: { borderWidth: 1, borderColor: "#ccc", borderRadius: 5, padding: 12, marginBottom: 10 },
  cardLabel: { fontSize: 14, color: "#555" },
  cardNumberBlue: { fontSize: 20, fontWeight: "bold", color: "#2980b9" },
  cardNumberRed: { fontSize: 20, fontWeight: "bold", color: "#c0392b" },
  cardNumberGreen: { fontSize: 20, fontWeight: "bold", color: "#27ae60" },
  tableContainer: { borderWidth: 1, borderColor: "#ccc", borderRadius: 5, padding: 10, marginTop: 10 },
  tableTitle: { fontSize: 16, fontWeight: "bold" },
  tableSubtitle: { fontSize: 12, color: "#555", marginBottom: 10 },
  tableHeader: { flexDirection: "row", justifyContent: "space-between", borderBottomWidth: 1, borderColor: "#ccc", paddingBottom: 5 },
  tableHeaderText: { fontSize: 10, fontWeight: "bold" },
  tableRow: { flexDirection: "row", justifyContent: "space-between", paddingVertical: 8, alignItems: "center" },
  tableCell: { fontSize: 10 },
  statusVencido: { fontSize: 10, color: "#c0392b", fontWeight: "bold" },
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "center", alignItems: "center" },
  modalBox: { backgroundColor: "#fff", padding: 20, borderRadius: 12, width: "85%" },
  modalTitle: { fontSize: 18, fontWeight: "bold", marginBottom: 10, textAlign: "center" },
  input: { borderWidth: 1, borderColor: "#ccc", borderRadius: 5, padding: 10, marginBottom: 10, fontSize: 14 },
  switchRow: { flexDirection: "row", alignItems: "center", marginBottom: 15 },
  primaryBtn: { backgroundColor: "#2f3640", padding: 10, borderRadius: 5, alignItems: "center", marginBottom: 10 },
  primaryBtnBlack: { backgroundColor: "#000", padding: 10, borderRadius: 5, alignItems: "center", marginBottom: 10 },
  primaryBtnText: { color: "#fff", fontWeight: "bold" },
  cancelBtn: { borderWidth: 1, borderColor: "#ccc", padding: 10, borderRadius: 5, alignItems: "center" },
});
