<template>
  <div class="form-page-container">
    <div class="form-card">
      <h1>¡Bienvenido de Nuevo!</h1>
      <p class="subtitle">Inicia sesión para acceder a tu cuenta de TourFer.</p>
      
      <form @submit.prevent="handleLogin">
        
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
            placeholder="Tu contraseña" 
            required
          >
        </div>
        
        <div v-if="authStore.error" class="error-message">
          {{ authStore.error }}
        </div>
        
        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 10px;">
          Ingresar
        </button>
        
      </form>
      
      <div class="form-footer">
        <p>¿No tienes cuenta? <router-link to="/register">Regístrate</router-link></p>
      </div>
      <div class="help-link">
        <a href="mailto:toufer2003@gmail.com?subject=Olvidé mi contraseña - TourFer">
          ¿Olvidaste tu contraseña? Contactar soporte
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'LoginView',
  data() {
    return {
      email: '',
      password: '',
      authStore: useAuthStore(),
    };
  },
  
  methods: {
    async handleLogin() {
      this.authStore.error = null;
      
      const loginExitoso = await this.authStore.login(this.email, this.password);
      
      if (loginExitoso) {
        if (this.authStore.isAdmin) {
          this.$router.push('/admin'); 
        } else {
          this.$router.push('/');
        }
      }
    }
  },
  
  unmounted() {
    this.authStore.error = null;
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