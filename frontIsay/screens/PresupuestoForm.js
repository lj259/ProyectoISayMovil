import React,{useState,useEffect} from 'react';
import { SafeAreaView, View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { Picker } from '@react-native-picker/picker';
const API_URL='http://192.168.1.65:8000';
export default function PresupuestoForm({route,navigation}){
  const editar=route.params?.presupuesto;
  const [monto,setMonto]=useState(editar?`${editar.monto}`:'');
  const [ano,setAno]=useState(editar?editar.ano:new Date().getFullYear());
  const [mes,setMes]=useState(editar?editar.mes:new Date().getMonth()+1);
  const [categoriaId,setCategoriaId]=useState(editar?editar.categoria_id:1);
  const [cats,setCats]=useState([]);
  useEffect(()=>{fetchCats();},[]);
  const fetchCats=async()=>{ try{ setCats(await (await fetch(`${API_URL}/categorias?tipo=gasto`)).json()); }catch(e){console.error(e);} };
  const guardar=async()=>{ if(!monto){Alert.alert('Error','El monto es obligatorio');return;} const payload={usuario_id:1,categoria_id:categoriaId,monto:parseFloat(monto),ano,mes}; const url=`${API_URL}/presupuestos${editar?'/'+editar.id:''}`; try{ const res=await fetch(url,{method:editar?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); if(!res.ok)throw new Error(); navigation.goBack(); }catch(e){Alert.alert('Error','No se pudo guardar el presupuesto');} };
  return(<SafeAreaView style={{flex:1,padding:16}}><View><Text>Monto</Text><TextInput style={styles.input} keyboardType="numeric" value={monto} onChangeText={setMonto}/><Text>Año</Text><TextInput style={styles.input} keyboardType="numeric" value={`${ano}`} onChangeText={v=>setAno(parseInt(v)||ano)}/><Text>Mes</Text><TextInput style={styles.input} keyboardType="numeric" value={`${mes}`} onChangeText={v=>setMes(parseInt(v)||mes)}/><Text>Categoría</Text><Picker selectedValue={categoriaId} onValueChange={setCategoriaId} style={styles.picker}>{cats.map(c=><Picker.Item key={c.id} label={c.nombre} value={c.id}/>)};</Picker><TouchableOpacity style={styles.button} onPress={guardar}><Text style={styles.buttonText}>{editar?'Actualizar':'Crear'}</Text></TouchableOpacity></View></SafeAreaView>);
}
const styles=StyleSheet.create({ input:{borderWidth:1,borderColor:'#ccc',borderRadius:6,padding:8,marginBottom:12}, picker:{marginBottom:12}, button:{backgroundColor:'#2ecc71',padding:12,borderRadius:6,alignItems:'center'}, buttonText:{color:'#fff',fontWeight:'bold'} });
