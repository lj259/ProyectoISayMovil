import 'react-native-gesture-handler';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

import Perfil from './screens/Perfil';
import EditarPerfil from './screens/EditarPerfil';
import Configuracion from './screens/Configuracion';



const Tab = createBottomTabNavigator();
const ProfileStack = createNativeStackNavigator();

function PerfilStackScreen() {
  return (
    <ProfileStack.Navigator>
      <ProfileStack.Screen 
        name="PerfilHome" 
        component={Perfil} 
        options={{ title: 'Mi Perfil' }} 
      />
      <ProfileStack.Screen 
        name="EditarPerfil" 
        component={EditarPerfil} 
        options={{ title: 'Editar Perfil' }} 
      />
      <ProfileStack.Screen 
        name="Configuracion" 
        component={Configuracion} 
        options={{ title: 'Configuración' }} 
      />
    </ProfileStack.Navigator>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarIcon: ({ color, size }) => {
            let iconName;
            switch (route.name) {
              case 'Home':
                iconName = 'home';
                break;
              case 'Perfil':
                iconName = 'person';
                break;
              case 'Configuracion':
                iconName = 'settings';
                break;
              default:
                iconName = 'alert';
            }
            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#2ecc71',
          tabBarInactiveTintColor: 'gray',
        })}
      >
        <Tab.Screen name="Perfil" component={PerfilStackScreen} />

      </Tab.Navigator>
    </NavigationContainer>
  );
}
