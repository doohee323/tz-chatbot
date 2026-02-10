<template>
  <div class="register-page">
    <div class="register-card">
      <h1>{{ $t('auth.register') }}</h1>
      <p class="subtitle">{{ $t('auth.registerSubtitle') }}</p>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">{{ $t('common.username') }}</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="form-input"
            :placeholder="$t('auth.loginIdPlaceholder')"
            required
          >
        </div>
        <div class="form-group">
          <label for="name">{{ $t('common.name') }}</label>
          <input
            id="name"
            v-model="name"
            type="text"
            class="form-input"
            :placeholder="$t('auth.namePlaceholder')"
            required
          >
        </div>
        <div class="form-group">
          <label for="email">{{ $t('common.email') }}</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="form-input"
            :placeholder="$t('auth.emailPlaceholder')"
            required
          >
        </div>
        <div class="form-group">
          <label for="password">{{ $t('common.password') }}</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-input"
            :placeholder="$t('auth.passwordPlaceholder')"
            required
            minlength="6"
          >
        </div>
        <div class="form-group">
          <label for="passwordConfirm">{{ $t('common.passwordConfirm') }}</label>
          <input
            id="passwordConfirm"
            v-model="passwordConfirm"
            type="password"
            class="form-input"
            :placeholder="$t('auth.passwordConfirmPlaceholder')"
            required
            minlength="6"
          >
        </div>
        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? $t('auth.registering') : $t('auth.registerButton') }}
        </button>
      </form>

      <p class="footer-note">
        {{ $t('auth.registerLink') }} <router-link to="/login">{{ $t('menu.login') }}</router-link>
      </p>
    </div>
  </div>
</template>

<script>
const TOKEN_KEY = 'admin_token'

export default {
  name: 'Register',
  data() {
    return {
      username: '',
      name: '',
      email: '',
      password: '',
      passwordConfirm: '',
      loading: false
    }
  },
  methods: {
    async handleRegister() {
      if (this.password.length < 6) {
        this.$toast.error(this.$t('auth.passwordMinLength'))
        return
      }
      if (this.password !== this.passwordConfirm) {
        this.$toast.error(this.$t('auth.passwordMismatch'))
        return
      }
      this.loading = true
      try {
        const r = await fetch('/v1/admin/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.username.trim(),
            name: this.name.trim(),
            email: this.email.trim().toLowerCase(),
            password: this.password,
            password_confirm: this.passwordConfirm
          })
        })
        if (!r.ok) {
          const data = await r.json().catch(() => ({}))
          const detail = Array.isArray(data.detail) ? data.detail[0]?.msg || data.detail : data.detail
          throw new Error(typeof detail === 'string' ? detail : this.$t('auth.registerFailed'))
        }
        const data = await r.json()
        const token = data.access_token
        if (!token) throw new Error(this.$t('auth.tokenError'))
        localStorage.setItem(TOKEN_KEY, token)
        this.$router.replace('/admin')
      } catch (e) {
        this.$toast.error(e.message || this.$t('auth.registerError'))
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.register-page {
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: var(--bg, #0f172a);
  color: #f1f5f9;
}
.register-card {
  width: 100%;
  max-width: 400px;
  background: var(--surface, #1e293b);
  border-radius: 12px;
  padding: 2rem;
  border: 1px solid rgba(255,255,255,0.06);
}
.register-card h1 { font-size: 1.5rem; margin: 0 0 0.5rem; color: #f1f5f9; }
.subtitle { color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem; }
.register-form { display: flex; flex-direction: column; gap: 1.25rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.form-group label { font-size: 0.85rem; font-weight: 600; color: #94a3b8; }
.form-input {
  padding: 0.6rem 0.9rem;
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 8px;
  background: #0f172a;
  color: #f1f5f9;
  font-size: 1rem;
}
.form-input:focus { outline: none; border-color: #38bdf8; }
.error-msg { color: #f87171; font-size: 0.9rem; margin: 0; }
.btn-submit {
  padding: 0.75rem 1rem;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-submit:hover:not(:disabled) { background: #1d4ed8; }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.footer-note {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255,255,255,0.06);
  font-size: 0.9rem;
  color: #94a3b8;
}
.footer-note a { color: #38bdf8; }
.footer-note a:hover { text-decoration: underline; }
</style>
