import Vue from 'vue'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import { installToast } from './plugins/toast'

Vue.config.productionTip = false
Vue.use(installToast)

new Vue({
  router,
  i18n,
  render: h => h(App)
}).$mount('#app')
