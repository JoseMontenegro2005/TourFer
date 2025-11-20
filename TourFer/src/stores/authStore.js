import { defineStore } from 'pinia';
import axios from 'axios';

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
    isAdmin: (state) => state.userRole === '1',
  },

  actions: {
    async login(email, password) {
      this.error = null;
      try {
        const response = await axios.post('https://tourfer-reservas.onrender.com/login', {
          email: email,
          password: password,
        });

        const token = response.data.access_token;
        const payload = decodeJwt(token);
        const rol = payload.rol_id.toString(); 

        this.token = token;
        this.userRole = rol;
        localStorage.setItem('token', token);
        localStorage.setItem('userRole', rol);

        return true; 
        
      } catch (e) {
        this.error = 'Error: Email o contraseña incorrectos.';
        console.error(e);
        return false;
      }
    },

    logout() {
      this.token = null;
      this.userRole = null;
      this.error = null;
      localStorage.removeItem('token');
      localStorage.removeItem('userRole');
    },

    getAuthHeaders() {
      if (this.token) {
        return { headers: { Authorization: `Bearer ${this.token}` } };
      }
      return {};
    }
  },
});
