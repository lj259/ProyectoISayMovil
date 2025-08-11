import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  ScrollView,
  View,
  Text,
  Dimensions,
  ActivityIndicator,
  StyleSheet
} from 'react-native';
import { LineChart, PieChart } from 'react-native-chart-kit';

const API_URL = 'http://192.168.1.65:8000';
const screenWidth = Dimensions.get('window').width;

export default function Home() {
  const [loading, setLoading] = useState(true);
  const [resumen, setResumen] = useState({
    total_ingresos: 0,
    total_egresos: 0,
    balance: 0
  });
  const [porCategoria, setPorCategoria] = useState([]);
  const [tendencias, setTendencias] = useState([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const resSum = await fetch(
          `${API_URL}/resumen?usuario_id=1`
        );
        setResumen(await resSum.json());

        const resCat = await fetch(
          `${API_URL}/graficas/categorias?tipo=gasto&usuario_id=1`
        );
        setPorCategoria(await resCat.json());

        const resTen = await fetch(
          `${API_URL}/graficas/tendencias?tipo=gasto&usuario_id=1`
        );
        setTendencias(await resTen.json());
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" />
      </SafeAreaView>
    );
  }

  const pieData = porCategoria.map((item) => ({
    name: item.categoria,
    population: item.total,
    color: `rgba(${Math.floor(Math.random() * 256)},${Math.floor(
      Math.random() * 256
    )},${Math.floor(Math.random() * 256)},0.7)`,
    legendFontColor: '#7F7F7F',
    legendFontSize: 12
  }));

  const lineData = {
    labels: tendencias.map((t) => t.mes),
    datasets: [{ data: tendencias.map((t) => t.total) }]
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#fff' }}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Resumen Financiero</Text>

        <View style={styles.summaryCard}>
          <Text>Ingresos: ${resumen.total_ingresos.toFixed(2)}</Text>
          <Text>Gastos: ${resumen.total_egresos.toFixed(2)}</Text>
          <Text>Balance: ${resumen.balance.toFixed(2)}</Text>
        </View>

        <Text style={styles.sectionTitle}>Gastos por Categoría</Text>
        <PieChart
          data={pieData}
          width={screenWidth - 32}
          height={220}
          chartConfig={chartConfig}
          accessor="population"
          backgroundColor="transparent"
          paddingLeft="15"
        />

        <Text style={styles.sectionTitle}>Tendencia Mensual de Gastos</Text>
        <LineChart
          data={lineData}
          width={screenWidth - 32}
          height={220}
          chartConfig={chartConfig}
        />
      </ScrollView>
    </SafeAreaView>
  );
}

const chartConfig = {
  backgroundGradientFrom: '#fff',
  backgroundGradientTo: '#fff',
  decimalPlaces: 2,
  color: () => `rgba(46,204,113,1)`,
  labelColor: () => '#333'
};

const styles = StyleSheet.create({
  container: {
    padding: 16
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8
  },
  summaryCard: {
    backgroundColor: '#ecf0f1',
    borderRadius: 8,
    padding: 12,
    marginBottom: 20
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 16,
    marginBottom: 8
  }
});
