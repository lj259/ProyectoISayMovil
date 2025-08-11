
import 'react-native-gesture-handler';
import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';

// Auth Screens
import Login from './screens/Login';
import Register from './screens/Register';
// Main Screens
import Home from './screens/Home';
import TransaccionesList from './screens/TransaccionesList';
import TransaccionForm from './screens/TransaccionForm';
import PresupuestosList from './screens/PresupuestosList';
import PresupuestoForm from './screens/PresupuestoForm';
import PagoFijosList from './screens/PagoFijosList';
import PagoFijoForm from './screens/PagoFijoForm';
import Perfil from './screens/Perfil';
import EditarPerfil from './screens/EditarPerfil';
import Configuracion from './screens/Configuracion';

const RootStack = createNativeStackNavigator();
const AuthStack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function AuthStackScreen() {
  return (
    <AuthStack.Navigator screenOptions={{ headerShown: false }}>
      <AuthStack.Screen name="Login" component={Login} />
      <AuthStack.Screen name="Register" component={Register} />
    </AuthStack.Navigator>
  );
}

function TransaccionesStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="TransaccionesList" component={TransaccionesList} options={{ title: 'Transacciones' }} />
      <Stack.Screen name="TransaccionForm" component={TransaccionForm} options={{ title: 'Formulario' }} />
    </Stack.Navigator>
  );
}

function PresupuestosStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="PresupuestosList" component={PresupuestosList} options={{ title: 'Presupuestos' }} />
      <Stack.Screen name="PresupuestoForm" component={PresupuestoForm} options={{ title: 'Formulario' }} />
    </Stack.Navigator>
  );
}

function PagoFijosStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="PagoFijosList" component={PagoFijosList} options={{ title: 'Pagos Fijos' }} />
      <Stack.Screen name="PagoFijoForm" component={PagoFijoForm} options={{ title: 'Formulario' }} />
    </Stack.Navigator>
  );
}

function PerfilStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="PerfilHome" component={Perfil} options={{ title: 'Mi Perfil' }} />
      <Stack.Screen name="EditarPerfil" component={EditarPerfil} options={{ title: 'Editar Perfil' }} />
      <Stack.Screen name="Configuracion" component={Configuracion} options={{ title: 'Configuración' }} />
    </Stack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ color, size }) => {
          let iconName;
          switch (route.name) {
            case 'Home': iconName = 'home'; break;
            case 'Transacciones': iconName = 'swap-horizontal'; break;
            case 'Presupuestos': iconName = 'reader'; break;
            case 'Pagos Fijos': iconName = 'cash'; break;
            case 'Perfil': iconName = 'person'; break;
            case 'Configuración': iconName = 'settings'; break;
          }
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2ecc71',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Home" component={Home} />
      <Tab.Screen name="Transacciones" component={TransaccionesStack} />
      <Tab.Screen name="Presupuestos" component={PresupuestosStack} />
      <Tab.Screen name="Pagos Fijos" component={PagoFijosStack} />
      <Tab.Screen name="Perfil" component={PerfilStack} />
      <Tab.Screen name="Configuración" component={Configuracion} />
    </Tab.Navigator>
  );
}

export default function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    AsyncStorage.getItem('userId').then(id => {
      setLoggedIn(!!id);
      setChecking(false);
    });
  }, []);

  if (checking) return null;

  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <RootStack.Navigator screenOptions={{ headerShown: false }}>
        {loggedIn ? (
          <RootStack.Screen name="Main" component={MainTabs} />
        ) : (
          <RootStack.Screen name="Auth" component={AuthStackScreen} />
        )}
      </RootStack.Navigator>
    </NavigationContainer>
  );
}