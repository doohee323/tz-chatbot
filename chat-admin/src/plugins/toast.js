/**
 * Toast plugin (tz-cointutor style).
 * Usage: this.$toast.success(msg), this.$toast.error(msg)
 */
import Vue from 'vue'

const state = Vue.observable({
  show: false,
  message: '',
  type: 'success', // success | error
  timer: null
})

function show(message, type = 'success', duration = 5000) {
  if (state.timer) {
    clearTimeout(state.timer)
  }
  state.message = message
  state.type = type
  state.show = true
  if (duration > 0) {
    state.timer = setTimeout(() => {
      state.show = false
      state.timer = null
    }, duration)
  }
}

function hide() {
  if (state.timer) {
    clearTimeout(state.timer)
    state.timer = null
  }
  state.show = false
}

export const toast = {
  success: (msg, duration) => show(msg, 'success', duration),
  error: (msg, duration) => show(msg, 'error', duration)
}

export function installToast(Vue) {
  Vue.prototype.$toast = toast
}

export { state as toastState, hide as hideToast }
