import { defineStore } from 'pinia';
import axios from 'axios';
// ¡ELIMINADO! Ya no hay 'import router from ...'

// (Función auxiliar para decodificar)
function decodeJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(function (c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error('Error al decodificar el token:', e);
    return null;
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    userRole: localStorage.getItem('userRole') || null,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.userRole === '1', // Compara con string
  },

  actions: {
    // CAMBIO CLAVE: La función ahora es 'async'
    async login(email, password) {
      this.error = null;
      try {
        const response = await axios.post('http://127.0.0.1:5002/login', {
          email: email,
          password: password,
        });

        const token = response.data.access_token;
        const payload = decodeJwt(token);
        const rol = payload.rol_id.toString(); // Convierte a string

        this.token = token;
        this.userRole = rol;
        localStorage.setItem('token', token);
        localStorage.setItem('userRole', rol);
        
        // CAMBIO CLAVE:
        // Ya no hay 'router.push'. Devolvemos 'true' para avisar que fue exitoso.
        return true; 
        
      } catch (e) {
        this.error = 'Error: Email o contraseña incorrectos.';
        console.error(e);
        // Devolvemos 'false' si falla.
        return false;
      }
    },

    logout() {
      this.token = null;
      this.userRole = null;
      this.error = null;
      localStorage.removeItem('token');
      localStorage.removeItem('userRole');
      // CAMBIO CLAVE:
      // Ya no hay 'router.push'.
    },

    getAuthHeaders() {
      if (this.token) {
        return { headers: { Authorization: `Bearer ${this.token}` } };
      }
      return {};
    }
  },
});