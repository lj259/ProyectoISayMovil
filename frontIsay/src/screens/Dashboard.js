import React, { useCallback, useState } from "react";
import { useFocusEffect } from "@react-navigation/native";
import { View, Text, StyleSheet, ScrollView, Dimensions } from "react-native";
import { BarChart, PieChart } from "react-native-chart-kit";
import { Picker } from "@react-native-picker/picker";
import { getResumen, getTendencias, getCategorias } from "../utils/api";

export default function Dashboard() {
  const [resumen, setResumen] = useState({ total_ingresos: 0, total_egresos: 0, total_ahorros: 0, balance: 0 });
  const [tendencias, setTendencias] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [tipo, setTipo] = useState("egreso"); // Gastos

useFocusEffect(
  useCallback(() => {
    const cargarDatos = async () => {
      const resumenData = await getResumen();
      setResumen(resumenData);

      const tendenciasData = await getTendencias(tipo);
      setTendencias(tendenciasData);

      const categoriasData = await getCategorias(tipo);
      setCategorias(categoriasData);
    };

    cargarDatos();
  }, [tipo]) // Se vuelve a ejecutar si cambia el tipo
);


  // Datos para la gráfica de barras
  const barData = {
    labels: tendencias.map((item) => item.mes),
    datasets: [{ data: tendencias.map((item) => item.total) }],
  };

  // Datos para la gráfica circular
  const pieData = categorias.map((item, index) => ({
    name: item.categoria,
    population: item.total,
    color: colores[index % colores.length],
    legendFontColor: "#333",
    legendFontSize: 12,
  }));

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
            <Text style={styles.title_logo}>
              <Text style={styles.titleGreen}>Lana</Text> App
            </Text>
      {/* Resumen financiero */}
      <View style={styles.cardContainer}>
        <View style={styles.card}>
          <Text style={styles.title}>Ingresos</Text>
          <Text style={styles.ingreso}>${resumen.total_ingresos.toFixed(2)}</Text>
        </View>
        <View style={styles.card}>
          <Text style={styles.title}>Gastos</Text>
          <Text style={styles.egreso}>${resumen.total_egresos.toFixed(2)}</Text>
        </View>
        <View style={styles.card}>
          <Text style={styles.title}>Ahorros</Text>
          <Text style={styles.ahorro}>${resumen.total_ahorros.toFixed(2)}</Text>
        </View>
        <View style={styles.card}>
          <Text style={styles.title}>Balance</Text>
          <Text style={styles.balance}>${resumen.balance.toFixed(2)}</Text>
        </View>
      </View>

      {/* Selector de tipo */}
      <Text style={styles.sectionTitle}>Seleccionar tipo de gráfica</Text>
      <Picker
        selectedValue={tipo}
        style={styles.picker}
        onValueChange={(itemValue) => setTipo(itemValue)}
      >
        <Picker.Item label="Gastos" value="egreso" />
        <Picker.Item label="Ingresos" value="ingreso" />
        <Picker.Item label="Ahorros" value="ahorro" />
      </Picker>

      {/* Tendencia (barras) */}
      <Text style={styles.sectionTitle}>Tendencia mensual</Text>
      <BarChart
        data={barData}
        width={Dimensions.get("window").width - 40}
        height={220}
        yAxisLabel="$"
        chartConfig={chartConfig}
        verticalLabelRotation={30}
        style={styles.chart}
      />

      {/* Distribución (circular) */}
      <Text style={styles.sectionTitle}>Distribución por categoría</Text>
      {categorias.length > 0 ? (
        <PieChart
          data={pieData}
          width={Dimensions.get("window").width - 40}
          height={220}
          accessor="population"
          backgroundColor="transparent"
          paddingLeft="15"
          chartConfig={chartConfig}
          absolute
        />
      ) : (
        <Text style={{ textAlign: "center", color: "#777" }}>
          No hay datos para mostrar en esta categoría
        </Text>
      )}

    </ScrollView>
  );
}

const colores = ["#4caf50", "#ff9800", "#2196f3", "#f44336", "#9c27b0"];

const chartConfig = {
  backgroundGradientFrom: "#fff",
  backgroundGradientTo: "#fff",
  color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
  labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
  style: { borderRadius: 16 },
  propsForDots: { r: "6", strokeWidth: "2", stroke: "#ffa726" },
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#fff" },
  cardContainer: { flexDirection: "row", justifyContent: "space-between", marginBottom: 20 },
  card: {
    flex: 1,
    backgroundColor: "#f5f5f5",
    marginHorizontal: 5,
    padding: 15,
    borderRadius: 10,
    alignItems: "center",
  },
  title: { fontSize: 14, color: "#777" },
  ingreso: { fontSize: 18, color: "#2ecc71", fontWeight: "bold" },
  egreso: { fontSize: 18, color: "#e74c3c", fontWeight: "bold" },
  ahorro: { fontSize: 18, color: "#ffc107", fontWeight: "bold" },
  balance: { fontSize: 18, color: "#2980b9", fontWeight: "bold" },
  sectionTitle: { fontSize: 16, fontWeight: "bold", marginVertical: 10 },
  chart: {borderRadius:16}, 
  picker: {marginVertical: 10, backgroundColor: "#f5f5f5", borderRadius: 8},
  title_logo: { fontSize: 28, fontWeight: "bold", marginBottom: 10 },
  titleGreen: { color: "#6ab04c" },
}); 