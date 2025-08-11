import React,{useState,useEffect} from 'react';
import { SafeAreaView, ScrollView, View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
const API_URL='http://192.168.1.65:8000';
export default function Perfil({navigation}) {
	const [usuario, setUsuario] = useState({ nombre_usuario: '', correo: '', telefono: '' });

	const fetchPerfil = async () => {
		try {
			const data = await (await fetch(`${API_URL}/usuarios/1`)).json();
			setUsuario({ nombre_usuario: data.nombre_usuario, correo: data.correo, telefono: data.telefono });
		} catch (e) {
			Alert.alert('Error', 'No se pudo cargar tu perfil');
		}
	};

	useEffect(() => {
		fetchPerfil();
	}, []);

	return (
		<SafeAreaView style={styles.container}>
			<ScrollView contentContainerStyle={styles.content}>
				<View style={styles.card}>
					<View style={styles.header}>
						<Text style={styles.title}>Mi Perfil</Text>
						<View style={styles.icons}>
							<TouchableOpacity onPress={() => navigation.navigate('EditarPerfil')}>
								<Ionicons name="pencil" size={24} style={styles.icon} />
							</TouchableOpacity>
							<TouchableOpacity onPress={() => navigation.navigate('Configuracion')}>
								<Ionicons name="settings" size={24} />
							</TouchableOpacity>
						</View>
					</View>
					<Text style={styles.label}>Usuario</Text>
					<Text style={styles.value}>{usuario.nombre_usuario}</Text>
					<Text style={styles.label}>Correo</Text>
					<Text style={styles.value}>{usuario.correo}</Text>
					<Text style={styles.label}>Teléfono</Text>
					<Text style={styles.value}>{usuario.telefono}</Text>
				</View>
			</ScrollView>
		</SafeAreaView>
	);
}
const styles = StyleSheet.create({
	container: { flex: 1, backgroundColor: '#fff' },
	content: { padding: 16 },
	card: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 16 },
	header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
	title: { fontSize: 18, fontWeight: 'bold' },
		icons: { flexDirection: 'row' },
	});