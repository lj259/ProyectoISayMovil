import React from "react";
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from "react-native";
import { Ionicons } from "@expo/vector-icons";

export default function PresupuestoScreen() {
  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <Text style={styles.title}>
        <Text style={styles.titleGreen}>Lana</Text> App
      </Text>

      {/* Tabs */}
      <View style={styles.tabs}>
        {["Dashboard", "Transacciones", "Presupuestos", "Pagos fijos", "Configuración"].map((tab, i) => (
          <Text
            key={i}
            style={[styles.tabText, tab === "Presupuestos" && styles.activeTab]}
          >
            {tab}
          </Text>
        ))}
      </View>

      {/* Title and subtitle */}
      <Text style={styles.sectionTitle}>Control de Presupuesto</Text>
      <Text style={styles.sectionSubtitle}>
        Gestiona tus gastos mensuales por categoría
      </Text>

      {/* Resumen del mes */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>Resumen del mes</Text>
          <TouchableOpacity style={styles.addButton}>
            <Ionicons name="add" size={20} color="#fff" />
            <Text style={styles.addButtonText}>Nuevo Presupuesto</Text>
          </TouchableOpacity>
        </View>
        <Text style={styles.cardLabel}>Estado general de tu presupuesto</Text>
        <Text style={styles.amount}>Total gastado</Text>
        <Text style={styles.amountValue}>$2,580</Text>
        <Text style={styles.amount}>Presupuesto total</Text>
        <Text style={styles.amountValueSmall}>$3,350</Text>

        {/* Progress bar */}
        <View style={styles.progressBarBg}>
          <View style={[styles.progressBarFill, { width: "77%" }]} />
        </View>
        <Text style={styles.progressText}>77.0% del presupuesto utilizado</Text>
      </View>

      {/* Alerts */}
      <View style={[styles.alertBox, { borderColor: "#f1c40f", backgroundColor: "#fff9e6" }]}>
        <Ionicons name="warning" size={20} color="#f39c12" style={{ marginRight: 5 }} />
        <Text style={styles.alertText}>
          <Text style={{ fontWeight: "bold" }}>Cerca del límite:</Text> Estás cerca de exceder el presupuesto en: <Text style={{ fontWeight: "bold" }}>Comida</Text>.
        </Text>
      </View>

      <View style={[styles.alertBox, { borderColor: "#e74c3c", backgroundColor: "#fdecea" }]}>
        <Ionicons name="warning" size={20} color="#c0392b" style={{ marginRight: 5 }} />
        <Text style={styles.alertText}>
          <Text style={{ fontWeight: "bold" }}>¡Presupuesto excedido!</Text> Has superado el límite en: <Text style={{ fontWeight: "bold" }}>Entretenimiento</Text>.
        </Text>
      </View>

      {/* Categorías */}
      <View style={styles.grid}>
        {/* Alimentación */}
        <View style={[styles.categoryCard, { borderColor: "#e67e22" }]}>
          <View style={styles.categoryHeader}>
            <Ionicons name="restaurant" size={20} color="#e67e22" />
            <TouchableOpacity>
              <Ionicons name="create-outline" size={18} color="black" />
            </TouchableOpacity>
          </View>
          <Text style={styles.categoryTitle}>Alimentación</Text>
          <Text style={styles.categoryDetail}>Gastado: $650   Límite: $800</Text>
          <Text style={styles.categoryProgress}>81.3% utilizado</Text>
        </View>

        {/* Transporte */}
        <View style={[styles.categoryCard, { borderColor: "#2980b9" }]}>
          <View style={styles.categoryHeader}>
            <Ionicons name="car" size={20} color="#2980b9" />
            <TouchableOpacity>
              <Ionicons name="create-outline" size={18} color="black" />
            </TouchableOpacity>
          </View>
          <Text style={styles.categoryTitle}>Transporte</Text>
          <Text style={styles.categoryDetail}>Gastado: $280   Límite: $400</Text>
          <Text style={{ color: "#27ae60" }}>Disponible: $120</Text>
        </View>

        {/* Entretenimiento */}
        <View style={[styles.categoryCard, { borderColor: "#9b59b6" }]}>
          <View style={styles.categoryHeader}>
            <Ionicons name="game-controller" size={20} color="#9b59b6" />
            <TouchableOpacity>
              <Ionicons name="create-outline" size={18} color="black" />
            </TouchableOpacity>
          </View>
          <Text style={styles.categoryTitle}>Entretenimiento</Text>
          <Text style={styles.categoryDetail}>Gastado: $220   Límite: $200</Text>
          <Text style={{ color: "#c0392b" }}>100% utilizado  Exceso: $20</Text>
        </View>

        {/* Servicios */}
        <View style={[styles.categoryCard, { borderColor: "#16a085" }]}>
          <View style={styles.categoryHeader}>
            <Ionicons name="flash" size={20} color="#16a085" />
            <TouchableOpacity>
              <Ionicons name="create-outline" size={18} color="black" />
            </TouchableOpacity>
          </View>
          <Text style={styles.categoryTitle}>Servicios</Text>
          <Text style={styles.categoryDetail}>Gastado: $280   Límite: $350</Text>
          <Text>80% utilizado</Text>
        </View>
      </View>
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
  sectionTitle: { fontSize: 20, fontWeight: "bold" },
  sectionSubtitle: { fontSize: 14, color: "#555", marginBottom: 15 },
  card: { borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 12, marginBottom: 15 },
  cardHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  cardTitle: { fontSize: 16, fontWeight: "bold" },
  addButton: { flexDirection: "row", alignItems: "center", backgroundColor: "#2f3640", paddingHorizontal: 10, paddingVertical: 6, borderRadius: 5 },
  addButtonText: { color: "#fff", marginLeft: 5, fontSize: 14 },
  cardLabel: { fontSize: 13, color: "#555", marginBottom: 5 },
  amount: { fontSize: 13, color: "#555" },
  amountValue: { fontSize: 20, fontWeight: "bold" },
  amountValueSmall: { fontSize: 16, fontWeight: "bold", marginBottom: 5 },
  progressBarBg: { height: 8, backgroundColor: "#ccc", borderRadius: 4, overflow: "hidden", marginVertical: 5 },
  progressBarFill: { height: 8, backgroundColor: "#000" },
  progressText: { fontSize: 12, color: "#555" },
  alertBox: { flexDirection: "row", borderWidth: 1, padding: 8, borderRadius: 5, marginBottom: 10, alignItems: "center" },
  alertText: { fontSize: 13, flex: 1 },
  grid: { flexDirection: "row", flexWrap: "wrap", justifyContent: "space-between" },
  categoryCard: { borderWidth: 2, borderRadius: 8, padding: 10, width: "48%", marginBottom: 10 },
  categoryHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  categoryTitle: { fontWeight: "bold", fontSize: 14, marginTop: 5 },
  categoryDetail: { fontSize: 12, marginTop: 3 },
  categoryProgress: { fontSize: 12, color: "#555" },
});
