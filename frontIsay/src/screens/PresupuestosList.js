import React,{useState,useEffect} from 'react';
import { SafeAreaView, FlatList, View, Text, TouchableOpacity, ActivityIndicator, StyleSheet } from 'react-native';
const API_URL='http://192.168.1.65:8000';
export default function PresupuestosList({navigation}){
  const [list,setList]=useState([]);
  const [loading,setLoading]=useState(true);
  useEffect(()=>{ const unsub=navigation.addListener('focus',fetchPresupuestos); return unsub; },[navigation]);
  const fetchPresupuestos=async()=>{ setLoading(true); try{ setList(await (await fetch(`${API_URL}/presupuestos`)).json()); }catch(e){console.error(e);}finally{setLoading(false);} };
  if(loading) return <ActivityIndicator style={{flex:1}} size="large"/>;
  return(
    <SafeAreaView style={{flex:1,padding:16}}>
      <TouchableOpacity style={styles.addButton} onPress={()=>navigation.navigate('PresupuestoForm')}><Text style={styles.addText}>Nuevo Presupuesto</Text></TouchableOpacity>
      <FlatList data={list} keyExtractor={i=>i.id.toString()} renderItem={({item})=>(
        <View style={styles.item}>
          <Text>{item.ano}/{item.mes}: ${item.monto}</Text>
          <View style={styles.actions}><TouchableOpacity onPress={()=>navigation.navigate('PresupuestoForm',{presupuesto:item})}><Text style={styles.link}>Editar</Text></TouchableOpacity><TouchableOpacity onPress={async()=>{await fetch(`${API_URL}/presupuestos/${item.id}`,{method:'DELETE'}); fetchPresupuestos();}}><Text style={[styles.link,{color:'red'}]}>Eliminar</Text></TouchableOpacity></View>
        </View>
      )}/>
    </SafeAreaView>
  );
}
const styles=StyleSheet.create({ addButton:{backgroundColor:'#2ecc71',padding:12,borderRadius:6,marginBottom:10,alignItems:'center'}, addText:{color:'#fff',fontWeight:'bold'}, item:{padding:12,borderBottomWidth:1,borderColor:'#ccc'}, actions:{flexDirection:'row',justifyContent:'flex-end'}, link:{marginLeft:16,color:'#2980b9'} });
