import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import Dashboard from './src/screens/Dashboard';
import Transacciones from './src/screens/Transacciones'; 
import InicioScreen from './src/screens/InicioScreen';
import RegistroScreen from './src/screens/RegistroScreen';
import LoginScreen from './src/screens/LoginScreen';
import PerfilScreen from './src/screens/PerfilScreen'; // Placeholder for Perfil screen
import EditarPerfilScreen from './src/screens/EditarPerfil'; // 
import ConfiguracionScreen from './src/screens/Configuracion'; // Pl


const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();
function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ color, size }) => {
          let iconName;
          if (route.name === 'Dashboard') iconName = 'stats-chart';
          else if (route.name === 'Transacciones') iconName = 'list';
          else if (route.name === 'Perfil') iconName = 'person';
          else if (route.name === 'Ajustes') iconName = 'settings';
          else if (route.name === 'Configuracion') iconName = 'cog';
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2ecc71',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Dashboard" component={Dashboard} />
      <Tab.Screen name="Transacciones" component={Transacciones} />
      <Tab.Screen name="Perfil" component={PerfilScreen} /> {/* Placeholder for Perfil screen */}
      <Tab.Screen name="Ajustes" component={EditarPerfilScreen} /> {/* Placeholder for Ajustes screen */}
      <Tab.Screen name="Configuracion" component={ConfiguracionScreen} /> {/* Placeholder for Configuracion screen */}
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Inicio" component={InicioScreen} />
        <Stack.Screen name="Registro" component={RegistroScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Dashboard" component={TabNavigator} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}