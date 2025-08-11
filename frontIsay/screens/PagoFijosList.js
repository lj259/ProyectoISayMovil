import React,{useState,useEffect} from 'react';
import { SafeAreaView, FlatList, View, Text, TouchableOpacity, ActivityIndicator, StyleSheet } from 'react-native';
const API_URL='http://192.168.1.65:8000';
export default function PagoFijosList({navigation}) {
	const [list, setList] = useState([]);
	const [loading, setLoading] = useState(true);

	const fetchList = async () => {
		setLoading(true);
		try {
			setList(await (await fetch(`${API_URL}/pagos-fijos`)).json());
		} catch (e) {
			console.error(e);
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		const unsub = navigation.addListener('focus', fetchList);
		return unsub;
	}, [navigation]);

	if (loading) return <ActivityIndicator style={{ flex: 1 }} size="large" />;
	return (
		<SafeAreaView style={{ flex: 1, padding: 16 }}>
			<TouchableOpacity style={styles.addButton} onPress={() => navigation.navigate('PagoFijoForm')}>
				<Text style={styles.addText}>Nuevo Pago Fijo</Text>
			</TouchableOpacity>
			<FlatList
				data={list}
				keyExtractor={item => item.id.toString()}
				renderItem={({ item }) => (
					<View style={styles.item}>
						<Text>{item.fecha}: ${item.monto} - {item.descripcion}</Text>
						<View style={styles.actions}>
							<TouchableOpacity onPress={() => navigation.navigate('PagoFijoForm', { pago: item })}>
								<Text style={styles.link}>Editar</Text>
							</TouchableOpacity>
							<TouchableOpacity onPress={async () => {
								await fetch(`${API_URL}/pagos-fijos/${item.id}`, { method: 'DELETE' });
								fetchList();
							}}>
								<Text style={[styles.link, { color: 'red' }]}>Eliminar</Text>
							</TouchableOpacity>
						</View>
					</View>
				)}
			/>
		</SafeAreaView>
	);
}
const styles = StyleSheet.create({
	addButton: { backgroundColor: '#2ecc71', padding: 12, borderRadius: 6, marginBottom: 10, alignItems: 'center' },
	addText: { color: '#fff', fontWeight: 'bold' },
	item: { padding: 12, borderBottomWidth: 1, borderColor: '#ccc' },
	actions: { flexDirection: 'row', justifyContent: 'flex-end' },
	link: { marginLeft: 16, color: '#2980b9' }
});
