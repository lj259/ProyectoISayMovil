import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import Dashboard from './src/screens/Dashboard';
import Transacciones from './src/screens/Transacciones'; 
import { Ionicons } from '@expo/vector-icons';
import InicioScreen from './src/screens/InicioScreen';
import RegistroScreen from './src/screens/RegistroScreen';
import LoginScreen from './src/screens/LoginScreen';

const Tab = createBottomTabNavigator();
import { createNativeStackNavigator } from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarIcon: ({ color, size }) => {
            let iconName;
            if (route.name === 'Dashboard') {
              iconName = 'stats-chart';
            } else if (route.name === 'Transacciones') {
              iconName = 'list';
            } else if (route.name === 'Inicio') {
              iconName = 'home';
            } else if (route.name === 'Registro') {
              iconName = 'person-add';
            } else if (route.name === 'Login') {
              iconName = 'log-in';
            }
            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#2ecc71',
          tabBarInactiveTintColor: 'gray',
        })}
      >
        <Tab.Screen name="Dashboard" component={Dashboard} />
        <Tab.Screen name="Transacciones" component={Transacciones} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
