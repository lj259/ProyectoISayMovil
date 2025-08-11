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
import { crearPagoFijo, getPagosFijos, actualizarPagoFijo, eliminarPagoFijo, getBalanceAlerta, getResumenFinanciero } from "../utils/api";
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function PagosFijosScreen() {
  const [modalAdd, setModalAdd] = useState(false);
  const [modalEdit, setModalEdit] = useState(false);
  const [modalDelete, setModalDelete] = useState(false);
  
  const [fechaVencimiento, setFechaVencimiento] = useState(new Date());
  const [mostrarFechaPicker, setMostrarFechaPicker] = useState(false);

  const [categorias, setCategorias] = useState([]);
  const [nombrePago, setNombrePago] = useState("");
  const [frecuencia, setFrecuencia] = useState('');
  const [monto, setMonto] = useState("");
  
  const [selectedCategory, setSelectedCategory] = useState('');
  const [pagos, setPagos] = useState([]);
  const [pagoSeleccionado, setPagoSeleccionado] = useState(null);

  const [balanceAlerta, setBalanceAlerta] = useState(null);
  const [resumenFinanciero, setResumenFinanciero] = useState({
  pagos_programados: 0,
  total_mensual: 0,
  balance_disponible: 0,
});

  const frecuencias = [
    { id: 'diario', nombre: 'Diario' },
    { id: 'semanal', nombre: 'Semanal' },
    { id: 'mensual', nombre: 'Mensual' },
    { id: 'anual', nombre: 'Anual' },
  ];

  const cargarResumenFinanciero = async () => {
    try {
      const usuario_id = parseInt(await AsyncStorage.getItem('usuario_id'));
      const data = await getResumenFinanciero(usuario_id);
      console.log("Datos de resumen financiero:", data);
      setResumenFinanciero(data);
    } catch (err) {
      console.error("Error al obtener resumen financiero:", err);
    }
  };

  useEffect(() => {
    cargarResumenFinanciero();
  }, []);


  const cargarBalance = async () => {
      try {
        const usuario_id = parseInt(await AsyncStorage.getItem('usuario_id'));
        const data = await getBalanceAlerta(usuario_id);
        console.log("Datos de balance:", data);
        setBalanceAlerta(data);
      } catch (err) {
        console.error("Error al obtener alerta de balance:", err);
      }
    };

  useEffect(() => {
    const cargarBalance = async () => {
      try {
        const usuario_id = parseInt(await AsyncStorage.getItem('usuario_id'));
        const data = await getBalanceAlerta(usuario_id);
        setBalanceAlerta(data);
      } catch (err) {
        console.error("Error al obtener alerta de balance:", err);
      }
    };

    cargarBalance();
  }, []);


  const cargarPagos = async () => {
      try {
        const data = await getPagosFijos();
        setPagos(data);
      } catch (error) {
        console.error('Error al cargar pagos fijos:', error);
      }
  };

  const handleGuardarPago = async () => {
    const usuario_id = parseInt(await AsyncStorage.getItem('usuario_id'));
    const nuevoPago = {
      descripcion: nombrePago,
      usuario_id: usuario_id,
      categoria_id: selectedCategory,
      frecuencia: frecuencia,
      monto: monto === "" ? 0 : parseFloat(monto),
      fecha: fechaVencimiento.toISOString().split("T")[0]
    };

    try {
      console.log("Guardando pago fijo:", nuevoPago);
      const response = await crearPagoFijo(nuevoPago);
      console.log("Respuesta del servidor:", response);
      setModalAdd(false);
      cargarPagos();
      cargarBalance();
      cargarResumenFinanciero();
    } catch (err) {
      console.error("Error al guardar pago:", err);
    }
  };

  const handleActualizarPago = async () => {
    if (!pagoSeleccionado) return;

    const usuario_id = parseInt(await AsyncStorage.getItem('usuario_id'));
    const datosActualizados = {
      descripcion: nombrePago,
      usuario_id,
      categoria_id: parseInt(selectedCategory),
      frecuencia,
      monto: monto === "" ? 0 : parseFloat(monto),
      fecha: fechaVencimiento.toISOString().split("T")[0]
    };

    try {
      await actualizarPagoFijo(pagoSeleccionado.id, datosActualizados);
      setModalEdit(false);
      setPagoSeleccionado(null);
      cargarBalance();
      cargarPagos();
      cargarResumenFinanciero();
    } catch (err) {
      console.error("Error al actualizar pago:", err);
    }
  };

  const handleEliminarPago = async () => {
    if (!pagoSeleccionado) return;

    try {
      await eliminarPagoFijo(pagoSeleccionado.id);
      setModalDelete(false);
      setPagoSeleccionado(null);
      cargarPagos();
      cargarBalance();
    } catch (err) {
      console.error("Error al eliminar pago:", err);
    }
  };


  const onSelect = (value) => {
    setSelectedCategory(value);
  };
  const onSelectFrecuencia = (value) => {
    setFrecuencia(value);
  };

    useEffect(() => {
    const cargarPagos = async () => {
      try {
        const data = await getPagosFijos();
        setPagos(data);
      } catch (error) {
        console.error('Error al cargar pagos fijos:', error);
      }
    };

    cargarPagos();
  }, []);
  
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

      {balanceAlerta?.alerta && (
        <View style={styles.alertBox}>
          <Ionicons name="warning" size={20} color="#a94442" style={{ marginRight: 5 }} />
          <Text style={styles.alertText}>
            <Text style={{ fontWeight: "bold" }}>Alerta de Presupuesto:</Text> Tu ahorro actual (${balanceAlerta.ahorro}) es insuficiente para cubrir los pagos fijos (${balanceAlerta.total_pagos_fijos}). Faltan ${balanceAlerta.faltante}.
          </Text>
        </View>
      )}


      {/* Cards */}
      <View style={styles.card}>
        <Text style={styles.cardLabel}>Pagos programados</Text>
        <Text style={styles.cardNumberBlue}>{resumenFinanciero.pagos_programados}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardLabel}>Total mensual</Text>
        <Text style={styles.cardNumberRed}>
          {resumenFinanciero.total_mensual !== null
            ? `$${resumenFinanciero.total_mensual.toFixed(2)}`
            : "$0.00"}
        </Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardLabel}>Balance Disponible</Text>
        <Text style={styles.cardNumberGreen}>
          {resumenFinanciero.balance_disponible !== null
            ? `$${resumenFinanciero.balance_disponible.toFixed(2)}`
            : "$0.00"}
        </Text>
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

        {pagos.map((pago) => (
          <View key={pago.id} style={styles.tableRow}>
            <Text style={styles.tableCell}>{pago.nombre || "—"}</Text>
            <Text style={styles.tableCell}>{pago.categoria?.nombre || pago.categoria_id}</Text>
            <Text style={styles.tableCell}>${pago.monto.toFixed(2)}</Text>
            <Text style={styles.tableCell}>{new Date(pago.fecha).toLocaleDateString()}</Text>
            <Text style={pago.estado === "Vencido" ? styles.statusVencido : styles.statusActivo}>
              {pago.estado || "Activo"}
            </Text>
            <Text style={styles.tableCell}>{pago.frecuencia || "—"}</Text>
            <View style={{ flexDirection: "row", gap: 8 }}>
              <TouchableOpacity onPress={() => {
                setPagoSeleccionado(pago);
                setNombrePago(pago.nombre || pago.descripcion || "");
                setMonto(pago.monto.toString());
                setSelectedCategory(pago.categoria_id || "");
                setFrecuencia(pago.frecuencia || "");
                setFechaVencimiento(new Date(pago.fecha));
                setModalEdit(true);
              }}>
                <Ionicons name="create-outline" size={18} color="black" />
              </TouchableOpacity>

              <TouchableOpacity onPress={() => {
                setPagoSeleccionado(pago);
                setModalDelete(true);
              }}>
                <Ionicons name="trash-outline" size={18} color="black" />
              </TouchableOpacity>

            </View>
          </View>
        ))}
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
                selectedValue={frecuencia}
                onValueChange={onSelectFrecuencia}
              >
                <Picker.Item label="Selecciona una frecuencia" value="" />
                {frecuencias.map((freq) => (
                  <Picker.Item key={freq.id} label={freq.nombre} value={freq.id} />
                ))}
              </Picker>
            </View>

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
            <TextInput placeholder="Nombre del Pago" style={styles.input} value={pagoSeleccionado?.nombre || ''} onChangeText={(text) => setPagoSeleccionado({ ...pagoSeleccionado, nombre: text })} />
            <TextInput
              placeholder="Monto"
              style={styles.input}
              keyboardType="numeric"
              value={monto}
              onChangeText={(text) => setMonto(text)}
            />

            <View style={styles.input}>
              <Picker
                selectedValue={frecuencia}
                onValueChange={onSelectFrecuencia}
              >
                <Picker.Item label="Selecciona frecuencia" value="" />
                {frecuencias.map((f) => (
                  <Picker.Item key={f.id} label={f.nombre} value={f.id} />
                ))}
              </Picker>
            </View>

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

            

            <TouchableOpacity style={styles.primaryBtnBlack} onPress={handleActualizarPago}>
              <Text style={styles.primaryBtnText}>Actualizar pago</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.cancelBtn} onPress={() => { setModalEdit(false); setPagoSeleccionado(null); }}>
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
            <TouchableOpacity style={styles.primaryBtnBlack} onPress={handleEliminarPago}>
              <Text style={styles.primaryBtnText}>Eliminar</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.cancelBtn} onPress={() => { setModalDelete(false); setPagoSeleccionado(null); }}>
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
