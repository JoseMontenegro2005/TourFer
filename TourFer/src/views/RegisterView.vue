<template>
  <div class="form-page-container">
    <div class="form-card">
      <h1>Crea tu Cuenta</h1>
      <p class="subtitle">Regístrate para empezar a reservar.</p>
      
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="nombre">Nombre Completo</label>
          <input 
            type="text" 
            id="nombre" 
            v-model="nombre" 
            placeholder="Tu nombre" 
            required
          >
        </div>
        
        <div class="form-group">
          <label for="email">Correo Electrónico</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            placeholder="tu@correo.com" 
            required
          >
        </div>
        
        <div class="form-group">
          <label for="password">Contraseña</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            placeholder="Crea una contraseña" 
            required
          >
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 10px;">
          Registrarme
        </button>
      </form>
      
      <div class="form-footer">
        <p>¿Ya tienes cuenta? <router-link to="/login">Inicia sesión</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'RegisterView',
  data() {
    return {
      nombre: '',
      email: '',
      password: '',
      error: null,
      authStore: useAuthStore(),
    };
  },
  
  methods: {
    async handleRegister() {
      this.error = null;
      try {
        await axios.post('http://127.0.0.1:5002/register', {
          nombre: this.nombre,
          email: this.email,
          password: this.password,
        });
        
        const loginExitoso = await this.authStore.login(this.email, this.password);
        
        if (loginExitoso) {
          this.$router.push('/'); 
        } else {
          this.$router.push('/login');
        }
        
      } catch (e) {
        this.error = 'Error al registrar la cuenta. El email ya podría existir.';
        console.error(e);
      }
    }
  }
};
</script>

<style scoped>
.form-page-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem 0;
}

.form-card {
  width: 90%;
  max-width: 420px;
  background-color: var(--bg-white);
  border-radius: var(--border-radius-large);
  box-shadow: var(--shadow-medium);
  padding: 2.5rem;
  text-align: center;
}

h1 {
  color: var(--text-color);
  margin-bottom: 10px;
  font-weight: 700;
}

.subtitle {
  color: var(--text-light);
  margin-bottom: 2rem;
  font-size: 1rem;
}

.btn-primary {
  width: 100%;
  margin-top: 10px;
  padding: 15px;
  font-size: 1.1rem;
}

.error-message {
  margin-top: -10px;
  margin-bottom: 15px;
}

.form-footer {
  margin-top: 1.5rem;
  font-size: 0.9rem;
}
.form-footer p {
  color: var(--text-muted);
}
.form-footer a {
  color: var(--primary-color);
  font-weight: 600;
  text-decoration: none;
}
.form-footer a:hover {
  text-decoration: underline;
}
</style>