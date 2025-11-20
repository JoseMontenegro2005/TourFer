<template>
  <div class="tours-container">
    <header class="tours-header">
      <h1>Explora Nuestros Tours Culturales</h1>
      <p>Descubre la auténtica Colombia con TourFer.</p>
    </header>

    <div v-if="isLoading" class="loading-state">
      <p>Cargando tours...</p>
    </div>

    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <div v-if="tours.length > 0" class="tours-grid">
      <div v-for="tour in tours" :key="tour.id" class="tour-card">
        
        <div class="tour-image">
          <img :src="tour.imagen_url" alt="Imagen del tour">
          <span class="tour-price">${{ parseFloat(tour.precio).toLocaleString('es-CO') }}</span>
        </div>
        
        <div class="tour-content">
          <span class="tour-destination">{{ tour.destino }}</span>
          <h3>{{ tour.nombre }}</h3>
          <p>{{ tour.descripcion.substring(0, 100) }}...</p>
        </div>

        <div class="tour-footer">
          <span>{{ tour.duracion_horas }} horas</span>
          <button @click="handleComprar(tour)" class="btn-comprar">
            Reservar Ahora
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'ClienteTours',
  
  data() {
    return {
      tours: [],
      isLoading: true,
      error: null,
      authStore: useAuthStore(),
    };
  },

  methods: {
    async fetchTours() {
      this.isLoading = true;
      try {
        const response = await axios.get('https://tourfer-reservas.onrender.com/public/tours');
        this.tours = response.data;
      } catch (e) {
        console.error(e);
        this.error = 'No se pudieron cargar los tours. Inténtelo más tarde.';
      } finally {
        this.isLoading = false;
      }
    },
    
    async handleComprar(tour) {
// 1. Verificar autenticación
      if (!this.authStore.isAuthenticated) {
        this.$router.push('/login');
        return;
      }

      // 2. Recolectar datos (Usamos prompt temporalmente)
      // Idealmente aquí abrirías un Modal <ReservaModal />
      const fecha = prompt("Ingrese la fecha de reserva (YYYY-MM-DD):", new Date().toISOString().split('T')[0]);
      if (!fecha) return; // Si cancela, no hacemos nada

      const personas = prompt("¿Número de personas?", "1");
      if (!personas) return;

      try {
        // 3. Preparar payload
        const datosReserva = {
          tour_id: tour.id,
          fecha: fecha,
          personas: parseInt(personas)
        };

        // 4. Enviar petición usando los headers del store
        // NOTA: authStore.getAuthHeaders() ya devuelve { headers: { Authorization: ... } }
        const url = 'https://tourfer-reservas.onrender.com/reservar'; // Ajusta si es local
        
        await axios.post(url, datosReserva, this.authStore.getAuthHeaders());

        // 5. Éxito
        alert(`¡Reserva confirmada para ${tour.nombre}! Revisa tu correo.`);

      } catch (error) {
        console.error(error);
        const msg = error.response?.data?.msg || "Error al conectar con el servidor";
        alert(`Error: ${msg}`);
      }
    }
  },

  mounted() {
    this.fetchTours();
  }
};
</script>

<style scoped>
.tours-container {
  max-width: 1400px;
  margin: 0 auto;
}

.tours-header {
  text-align: center;
  margin-bottom: 2.5rem;
}
.tours-header h1 {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}
.tours-header p {
  font-size: 1.25rem;
  color: var(--text-light);
  margin-top: 0;
}

.tours-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem; 
}

.tour-card {
  background-color: var(--bg-white);
  border-radius: var(--border-radius-large);
  box-shadow: var(--shadow-medium);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.tour-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-large);
}

.tour-image {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
}

.tour-image img {
  width: 100%;
  height: 100%;
  object-fit: cover; 
}

.tour-price {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  background-color: rgba(8, 108, 20, 0.9);
  color: white;
  padding: 8px 12px;
  border-radius: var(--border-radius-medium);
  font-weight: 700;
  font-size: 1.1rem;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.tour-content {
  padding: 1.5rem;
  flex-grow: 1; 
}

.tour-destination {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--primary-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tour-content h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0.5rem 0;
}

.tour-content p {
  font-size: 0.95rem;
  color: var(--text-light);
  line-height: 1.5;
  margin: 0;
}

.tour-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 500;
}

.btn-comprar {
  padding: 8px 16px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius-medium);
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s;
}
.btn-comprar:hover {
  background-color: var(--primary-dark);
}
</style>
