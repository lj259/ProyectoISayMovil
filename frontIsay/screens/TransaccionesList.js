import React, { useState, useEffect } from 'react';
import { SafeAreaView, FlatList, View, Text, TouchableOpacity, ActivityIndicator, StyleSheet } from 'react-native';
const API_URL = 'http://192.168.1.65:8000';
export default function TransaccionesList({ navigation }) {
  const [trans, setTrans] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', fetchTrans);
    return unsubscribe;
  }, [navigation]);
  const fetchTrans = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/transacciones`);
      setTrans(await res.json());
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };
  if (loading) return <ActivityIndicator style={{flex:1}} size="large"/>;
  return (
    <SafeAreaView style={{flex:1,padding:16}}>
      <TouchableOpacity style={styles.addButton} onPress={()=>navigation.navigate('TransaccionForm')}><Text style={styles.addText}>Nueva Transacción</Text></TouchableOpacity>
      <FlatList data={trans} keyExtractor={item=>item.id.toString()} renderItem={({item})=>(
        <View style={styles.item}>
          <Text>{item.tipo.toUpperCase()}: ${item.monto} - {item.descripcion}</Text>
          <View style={styles.actions}>
            <TouchableOpacity onPress={()=>navigation.navigate('TransaccionForm',{transaccion:item})}><Text style={styles.link}>Editar</Text></TouchableOpacity>
            <TouchableOpacity onPress={async()=>{ await fetch(`${API_URL}/transacciones/${item.id}`,{method:'DELETE'}); fetchTrans(); }}><Text style={[styles.link,{color:'red'}]}>Eliminar</Text></TouchableOpacity>
          </View>
        </View>
      )}/>
    </SafeAreaView>
  );
}
const styles=StyleSheet.create({ addButton:{backgroundColor:'#2ecc71',padding:12,borderRadius:6,marginBottom:10,alignItems:'center'}, addText:{color:'#fff',fontWeight:'bold'}, item:{padding:12,borderBottomWidth:1,borderColor:'#ccc'}, actions:{flexDirection:'row',justifyContent:'flex-end'}, link:{marginLeft:16,color:'#2980b9'} });
