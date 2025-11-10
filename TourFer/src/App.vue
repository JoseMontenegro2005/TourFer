<template>
  <header>
    <nav class="navbar">
      <div class="navbar-brand">
        <router-link to="/">
          TourFer
        </router-link>
      </div>
      <div class="nav-links">
        <router-link to="/">Ver Tours</router-link>
        
        <router-link v-if="authStore.isAdmin" to="/admin">Panel Admin</router-link>
        
        <router-link v-if="authStore.isAuthenticated" to="/mis-reservas">Mis Reservas</router-link>
        
        <router-link v-if="!authStore.isAuthenticated" to="/login" class="nav-button login">
          Login
        </router-link>
        
        <a v-if="authStore.isAuthenticated" @click="handleLogout" class="nav-button logout">
          Cerrar Sesión
        </a>
      </div>
    </nav>
  </header>

  <main class="main-content">
    <router-view />
  </main>
</template>

<script>
import { RouterLink, RouterView } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'App',
  components: {
    RouterLink,
    RouterView
  },
  
  data() {
    return {
      authStore: useAuthStore()
    }
  },

  methods: {
    handleLogout() {
      this.authStore.logout();
      this.$router.push('/login');
    }
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2.5rem;
  background-color: var(--bg-white);
  box-shadow: var(--shadow-medium);
  border-bottom: 1px solid var(--border-color);
  font-family: var(--font-primary);
  position: sticky;
  top: 0;
  z-index: 1000;
  height: 80px; 
}

.navbar-brand a {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--primary-color);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-links a {
  text-decoration: none;
  color: var(--text-light);
  font-weight: 600;
  font-size: 1rem;
  padding-bottom: 5px;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.nav-links a.router-link-exact-active {
  border-bottom-color: var(--primary-color);
}

.nav-links a:not(.nav-button):hover {
  color: var(--primary-color);
}

.nav-button {
  padding: 8px 16px;
  border-radius: var(--border-radius-medium);
  cursor: pointer;
  border: 2px solid transparent;
}

.nav-button.login {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}
.nav-button.login:hover {
  background-color: var(--primary-dark);
  border-color: var(--primary-dark);
}

.nav-button.logout {
  background-color: transparent;
  color: var(--danger-color);
  border-color: var(--danger-color);
}
.nav-button.logout:hover {
  background-color: var(--danger-color);
  color: white;
}
</style>