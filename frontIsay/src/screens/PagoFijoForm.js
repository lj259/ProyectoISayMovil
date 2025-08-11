import React,{useState} from 'react';
import { SafeAreaView, View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
const API_URL='http://192.168.1.65:8000';
export default function PagoFijoForm({route, navigation}) {
	const editar = route.params?.pago;
	const [descripcion, setDescripcion] = useState(editar ? editar.descripcion : '');
	const [monto, setMonto] = useState(editar ? `${editar.monto}` : '');
	const [fecha, setFecha] = useState(editar ? new Date(editar.fecha) : new Date());
	const [showPicker, setShowPicker] = useState(false);

	const onChange = (e, sd) => {
		setShowPicker(false);
		sd && setFecha(sd);
	};

	const guardar = async () => {
		if (!monto || !descripcion) {
			Alert.alert('Error', 'Completa todos los campos');
			return;
		}
		const payload = {
			usuario_id: 1,
			descripcion,
			monto: parseFloat(monto),
			fecha: fecha.toISOString().split('T')[0]
		};
		const url = `${API_URL}/pagos-fijos${editar ? '/' + editar.id : ''}`;
		try {
			await fetch(url, {
				method: editar ? 'PUT' : 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});
			navigation.goBack();
		} catch (e) {
			Alert.alert('Error', 'No se pudo guardar');
		}
	};

	return (
		<SafeAreaView style={{ flex: 1, padding: 16 }}>
			<View>
				<Text>Descripción</Text>
				<TextInput style={styles.input} value={descripcion} onChangeText={setDescripcion} />
				<Text>Monto</Text>
				<TextInput style={styles.input} keyboardType="numeric" value={monto} onChangeText={setMonto} />
				<Text>Fecha</Text>
				<TouchableOpacity style={styles.input} onPress={() => setShowPicker(true)}>
					<Text>{fecha.toISOString().split('T')[0]}</Text>
				</TouchableOpacity>
				{showPicker && (
					<DateTimePicker value={fecha} mode="date" display="default" onChange={onChange} />
				)}
				<TouchableOpacity style={styles.button} onPress={guardar}>
					<Text style={styles.buttonText}>{editar ? 'Actualizar' : 'Crear'}</Text>
				</TouchableOpacity>
			</View>
		</SafeAreaView>
	);
}
const styles = StyleSheet.create({
	input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 6, padding: 8, marginBottom: 12 },
	button: { backgroundColor: '#2ecc71', padding: 12, borderRadius: 6, alignItems: 'center' },
	buttonText: { color: '#fff', fontWeight: 'bold' }
});
