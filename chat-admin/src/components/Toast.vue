<template>
  <div v-if="toastState.show" class="toast-notification" :class="toastClass">
    <div class="toast-content">
      <span>{{ toastState.message }}</span>
    </div>
    <button type="button" class="toast-close" @click="hide">&times;</button>
  </div>
</template>

<script>
import { toastState, hideToast } from '@/plugins/toast'

export default {
  name: 'Toast',
  data() {
    return { toastState }
  },
  computed: {
    toastClass() {
      return this.toastState.type === 'error' ? 'toast-error' : 'toast-success'
    }
  },
  methods: {
    hide() {
      hideToast()
    }
  }
}
</script>

<style scoped>
.toast-notification {
  position: fixed;
  top: 72px;
  right: 20px;
  z-index: 1055;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  min-width: 280px;
  max-width: 400px;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: #1e293b;
}
.toast-notification.toast-success { border-left: 4px solid #22c55e; }
.toast-notification.toast-error { border-left: 4px solid #f87171; }
.toast-content { flex: 1; font-size: 0.9rem; color: #e2e8f0; }
.toast-close {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  padding: 0.25rem;
}
.toast-close:hover { color: #fff; }
</style>
