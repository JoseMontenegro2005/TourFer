import { defineStore } from 'pinia';
import axios from 'axios';

function decodeJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    userRole: localStorage.getItem('userRole') || null,
    // NUEVO: Estado para el nombre
    userName: localStorage.getItem('userName') || null, 
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
        // Asegúrate que esta URL sea la de producción en Render
        const response = await axios.post('https://tourfer-reservas.onrender.com/login', {
          email: email,
          password: password,
        });

        const token = response.data.access_token;
        // NUEVO: Recibimos el nombre desde el backend
        const nombre = response.data.user_name; 
        
        const payload = decodeJwt(token);
        const rol = payload.rol_id.toString(); 

        this.token = token;
        this.userRole = rol;
        this.userName = nombre; // Guardamos en estado

        localStorage.setItem('token', token);
        localStorage.setItem('userRole', rol);
        localStorage.setItem('userName', nombre); // Guardamos en localStorage

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
      this.userName = null;
      this.error = null;
      localStorage.removeItem('token');
      localStorage.removeItem('userRole');
      localStorage.removeItem('userName'); // Limpiamos nombre
    },

    getAuthHeaders() {
      if (this.token) {
        return { headers: { Authorization: `Bearer ${this.token}` } };
      }
      return {};
    }
  },
});