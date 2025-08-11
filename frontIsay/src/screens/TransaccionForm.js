import React,{useState,useEffect} from 'react';
import { SafeAreaView, View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { Picker } from '@react-native-picker/picker';
const API_URL = 'http://192.168.1.65:8000';
export default function TransaccionForm({ route, navigation }) {
  const editar = route.params?.transaccion;
  const [monto,setMonto]=useState(editar?`${editar.monto}`:'');
  const [descripcion,setDescripcion]=useState(editar?editar.descripcion:'');
  const [tipo,setTipo]=useState(editar?editar.tipo:'gasto');
  const [categoriaId,setCategoriaId]=useState(editar?editar.categoria_id:1);
  const [categorias,setCategorias]=useState([]);
  useEffect(()=>{fetchCategorías();},[]);
  const fetchCategorías=async()=>{ try{ setCategorias(await (await fetch(`${API_URL}/categorias`)).json()); }catch(e){console.error(e);} };  
  const guardar=async()=>{
    if(!monto){Alert.alert('Error','El monto es obligatorio');return;}
    const payload={usuario_id:1,monto:parseFloat(monto),categoria_id:categoriaId,tipo,fecha:new Date().toISOString().split('T')[0],descripcion};
    const url=`${API_URL}/transacciones${editar?'/'+editar.id:''}`;
    try{ const res=await fetch(url,{method:editar?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); if(!res.ok)throw new Error(); navigation.goBack(); }catch(e){Alert.alert('Error','No se pudo guardar la transacción');}
  };
  return(
    <SafeAreaView style={{flex:1,padding:16}}>
      <View>
        <Text>Monto</Text>
        <TextInput style={styles.input} keyboardType="numeric" value={monto} onChangeText={setMonto}/>
        <Text>Tipo</Text>
        <Picker selectedValue={tipo} onValueChange={setTipo} style={styles.picker}><Picker.Item label="Ingreso" value="ingreso"/><Picker.Item label="Gasto" value="gasto"/></Picker>
        <Text>Categoría</Text>
        <Picker selectedValue={categoriaId} onValueChange={setCategoriaId} style={styles.picker}>{categorias.map(c=><Picker.Item key={c.id} label={`${c.nombre} (${c.tipo})`} value={c.id}/>)};</Picker>
        <Text>Descripción</Text>
        <TextInput style={styles.input} value={descripcion} onChangeText={setDescripcion}/>
        <TouchableOpacity style={styles.button} onPress={guardar}><Text style={styles.buttonText}>{editar?'Actualizar':'Crear'}</Text></TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}
const styles=StyleSheet.create({ input:{borderWidth:1,borderColor:'#ccc',borderRadius:6,padding:8,marginBottom:12}, picker:{marginBottom:12}, button:{backgroundColor:'#2ecc71',padding:12,borderRadius:6,alignItems:'center'}, buttonText:{color:'#fff',fontWeight:'bold'} });
