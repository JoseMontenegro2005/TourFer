<template>
  <div class="tours-container">
    <header class="tours-header">
      <h1>Explora Nuestros Tours Culturales</h1>
      <p>Descubre la auténtica Colombia con TourFer.</p>
    </header>

    <!-- Estados de Carga y Error -->
    <div v-if="isLoading" class="loading-state">
      <p>Cargando tours...</p>
    </div>

    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <!-- GRID DE TOURS -->
    <div v-if="tours.length > 0" class="tours-grid">
      <div v-for="tour in tours" :key="tour.id" class="tour-card">
        
        <div class="tour-image">
          <img :src="tour.imagen_url || 'https://via.placeholder.com/400x300'" alt="Imagen del tour">
          <span class="tour-price">${{ parseFloat(tour.precio).toLocaleString('es-CO') }}</span>
        </div>
        
        <div class="tour-content">
          <span class="tour-destination">{{ tour.destino }}</span>
          <h3>{{ tour.nombre }}</h3>
          <p>{{ tour.descripcion ? tour.descripcion.substring(0, 100) + '...' : 'Sin descripción' }}</p>
          
          <div style="margin-top: 1rem; display: flex; justify-content: space-between; font-size: 0.85rem; color: #666;">
             <span>🕒 {{ tour.duracion_horas }} Horas</span>
             <span>👥 {{ tour.cupos_disponibles }} Cupos</span>
          </div>
        </div>

        <div class="tour-footer">
          <button @click="abrirModalReserva(tour)" class="btn-comprar">
            Reservar Ahora
          </button>
        </div>
      </div>
    </div>

    <!-- ========================================= -->
    <!-- MODAL DE RESERVA -->
    <!-- ========================================= -->
    <div v-if="showModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Reservar: {{ selectedTour?.nombre }}</h2>
          <button class="btn-close" @click="cerrarModal">×</button>
        </div>

        <form @submit.prevent="enviarReserva" class="reserva-form">
          <div class="form-group">
            <label>Fecha de Reserva:</label>
            <!-- Se aplica minDate aquí para bloquear fechas anteriores -->
            <input 
              type="date" 
              v-model="formReserva.fecha" 
              required 
              :min="minDate"
            >
            <small style="color: #666; font-size: 0.8em;">Solo reservas con 15 días de anticipación</small>
          </div>

          <div class="form-group">
            <label>Cantidad de Personas:</label>
            <input 
              type="number" 
              v-model.number="formReserva.personas" 
              min="1" 
              :max="selectedTour?.cupos_disponibles"
              required
            >
            <small v-if="selectedTour" style="color: #666;">Máximo {{ selectedTour.cupos_disponibles }} personas</small>
          </div>

          <div class="reserva-summary" v-if="selectedTour">
            <p><strong>Precio por persona:</strong> ${{ parseFloat(selectedTour.precio).toLocaleString('es-CO') }}</p>
            <div class="total-highlight">
              <span>Total a Pagar:</span>
              <span>${{ (selectedTour.precio * formReserva.personas).toLocaleString('es-CO') }}</span>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="cerrarModal">Cancelar</button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'Procesando...' : 'Confirmar Reserva' }}
            </button>
          </div>
        </form>
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
      
      showModal: false,
      selectedTour: null,
      isSubmitting: false,
      formReserva: {
        fecha: '',
        personas: 1
      }
    };
  },

  computed: {
    // LÓGICA MODIFICADA PARA REGLA DE 15 DÍAS
    minDate() {
      const fechaMinima = new Date();
      // Sumamos 15 días a la fecha actual
      fechaMinima.setDate(fechaMinima.getDate() + 15);
      // Formateamos a YYYY-MM-DD para el input HTML
      return fechaMinima.toISOString().split('T')[0];
    }
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
    
    abrirModalReserva(tour) {
      if (!this.authStore.isAuthenticated) {
        alert("Por favor inicia sesión para reservar.");
        this.$router.push('/login');
        return;
      }
      this.selectedTour = tour;
      this.formReserva = { fecha: '', personas: 1 };
      this.showModal = true;
    },

    cerrarModal() {
      this.showModal = false;
      this.selectedTour = null;
    },

    async enviarReserva() {
      this.isSubmitting = true;
      try {
        const datosReserva = {
          tour_id: this.selectedTour.id,
          fecha: this.formReserva.fecha,
          personas: this.formReserva.personas
        };
        
        const url = 'https://tourfer-reservas.onrender.com/reservas';
        
        await axios.post(url, datosReserva, this.authStore.getAuthHeaders());

        alert(`¡Reserva exitosa! Te hemos enviado un correo de confirmación.`);
        this.cerrarModal();
        this.fetchTours();

      } catch (error) {
        console.error(error);
        const msg = error.response?.data?.error || error.response?.data?.msg || "Error al conectar con el servidor";
        alert(`Error: ${msg}`);
      } finally {
        this.isSubmitting = false;
      }
    }
  },

  mounted() {
    this.fetchTours();
  }
};
</script>

<style scoped>
/* --- TUS ESTILOS ORIGINALES SE MANTIENEN --- */
.tours-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.tours-header {
  text-align: center;
  margin-bottom: 2.5rem;
}
.tours-header h1 {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-color, #333);
  margin-bottom: 0.5rem;
}
.tours-header p {
  font-size: 1.25rem;
  color: var(--text-light, #666);
  margin-top: 0;
}

.tours-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem; 
}

.tour-card {
  background-color: var(--bg-white, #fff);
  border-radius: var(--border-radius-large, 12px);
  box-shadow: var(--shadow-medium, 0 4px 6px rgba(0,0,0,0.1));
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  border: 1px solid #eee;
}

.tour-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-large, 0 10px 15px rgba(0,0,0,0.1));
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
  border-radius: var(--border-radius-medium, 8px);
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
  color: var(--primary-color, #2c3e50);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tour-content h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-color, #333);
  margin: 0.5rem 0;
}

.tour-content p {
  font-size: 0.95rem;
  color: var(--text-light, #666);
  line-height: 1.5;
  margin: 0;
}

.tour-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color, #eee);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: var(--text-muted, #888);
  font-weight: 500;
}

.btn-comprar {
  padding: 8px 16px;
  background-color: var(--primary-color, #2c3e50);
  color: white;
  border: none;
  border-radius: var(--border-radius-medium, 6px);
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s;
  width: 100%;
}
.btn-comprar:hover {
  background-color: var(--primary-dark, #1a252f);
}

/* ESTILOS DEL MODAL */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(3px);
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 1rem;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.4rem;
  color: var(--text-color, #333);
  font-weight: 700;
}

.btn-close {
  background: none;
  border: none;
  font-size: 2rem;
  line-height: 1;
  cursor: pointer;
  color: #999;
  padding: 0 0.5rem;
  transition: color 0.2s;
}
.btn-close:hover {
  color: #333;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-color, #333);
  font-size: 0.95rem;
}

.form-group input {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 2px solid #eee;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus {
  border-color: var(--primary-color, #2c3e50);
  outline: none;
}

.reserva-summary {
  background: #f8f9fa;
  padding: 1.25rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border: 1px solid #eee;
}

.total-highlight {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #ddd;
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--primary-color, #2c3e50);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-primary {
  flex: 2;
  background: var(--primary-color, #2c3e50);
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  font-size: 1rem;
  transition: opacity 0.2s;
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-secondary {
  flex: 1;
  background: #f1f3f5;
  color: #495057;
  border: none;
  padding: 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.btn-secondary:hover {
  background: #e9ecef;
}

.loading-state, .error-message {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #666;
}
.error-message {
  color: #e74c3c;
}
</style>