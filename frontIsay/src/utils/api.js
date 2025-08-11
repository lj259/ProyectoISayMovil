import axios from 'axios';

const API_URL = 'http://192.168.1.140:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

//Registro
export const register = async (form) => {
  try {
    const response = await api.post('/register', form);
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || 'Error al registrar usuario';
  }
};

// Función para login
export const login = async (correo, contraseña_hash) => {
  try {
    const response = await api.post('/login', { correo, contraseña_hash });
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || 'Error al iniciar sesión';
  }
};

//Dashboard
export const getResumen = async () => {
  const response = await api.get('/resumen');
  return response.data;
};

export const getTendencias = async (tipo) => {
  const response = await api.get(`/graficas/tendencias?tipo=${tipo}`);
  return response.data;
};

export const getCategorias = async (tipo) => {
  const response = await api.get(`/graficas/categorias?tipo=${tipo}`);
  return response.data;
};

//Transacciones
export const getTransacciones = async () => {
  const response = await api.get('/transacciones');
  return response.data;
};

export const crearTransaccion = async (data) => {
  const response = await api.post('/transacciones', data);
  return response.data;
};

export const editarTransaccion = async (id, data) => {
  const response = await api.put(`/transacciones/${id}`, data);
  return response.data;
};

export const eliminarTransaccion = async (id) => {
  const response = await api.delete(`/transacciones/${id}`);
  return response.data;
};
export default api;
