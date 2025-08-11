import axios from 'axios';

const API_URL = 'http://10.16.37.152:8000';

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
export const getResumen = async (usuario_id) => {
  const response = await api.get(`/resumen?usuario_id=${usuario_id}`);
  return response.data;
};

export const getTendencias = async (tipo, usuario_id) => {
  const response = await api.get(`/graficas/tendencias?tipo=${tipo}&usuario_id=${usuario_id}`);
  return response.data;
};

export const getCategorias = async (tipo, usuario_id) => {
  const response = await api.get(`/graficas/categorias?tipo=${tipo}&usuario_id=${usuario_id}`);
  return response.data;
};

//Transacciones
export const getTransacciones = async (usuario_id) => {
  const response = await api.get(`/transacciones?usuario_id=${usuario_id}`);
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

export const fetchCategorias = async () => {
  const response = await api.get('/categorias');
  return response.data;
};

// Pagos Fijos
export const crearPagoFijo = async (data) => {
  try {
    const response = await api.post('/pagos-fijos', data);
    console.log("Pago fijo creado:", response.data);
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || 'Error al crear pago fijo';
  }
};

export const getPagosFijos = async () => {
  try {
    const response = await api.get('/pagos-fijos');
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || 'Error al obtener pagos fijos';
  }
};

export const actualizarPagoFijo = async (id, data) => {
  try {
    const response = await api.put(`/pagos-fijos/${id}`, data);
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || 'Error al actualizar pago fijo';
  }
};

export const eliminarPagoFijo = async (id) => {
  try {
    const response = await api.delete(`/pagos-fijos/${id}`);
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || 'Error al eliminar pago fijo';
  }
};

export const getBalanceAlerta = async (usuario_id) => {
  const response = await fetch(`${API_URL}/pagos-fijos/${usuario_id}/balance-alerta`);
  if (!response.ok) throw new Error("Error al obtener balance");
  return await response.json();
};

export const getResumenFinanciero = async (usuario_id) => {
  try {
    const response = await api.get(`/resumen-financiero`, {
      params: { usuario_id }
    });
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || 'Error al obtener resumen financiero';
  }
};


export default api;
