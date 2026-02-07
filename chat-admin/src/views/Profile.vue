<template>
  <div class="profile-page">
    <div class="profile-card">
      <h1>{{ $t('profile.title') }}</h1>
      <p class="subtitle">{{ $t('profile.subtitle') }}</p>

      <section v-if="profile" class="profile-section">
        <h2>{{ $t('profile.basicInfo') }}</h2>
        <form @submit.prevent="handleUpdateProfile" class="profile-form">
          <div class="form-group">
            <label for="username">{{ $t('common.username') }}</label>
            <input
              id="username"
              :value="profile.username"
              type="text"
              class="form-input form-input-readonly"
              disabled
            >
          </div>
          <div class="form-group">
            <label for="name">{{ $t('common.name') }}</label>
            <input
              id="name"
              v-model="profileForm.name"
              type="text"
              class="form-input"
              :placeholder="$t('common.name')"
              maxlength="128"
            >
          </div>
          <div class="form-group">
            <label for="email">{{ $t('common.email') }}</label>
            <input
              id="email"
              v-model="profileForm.email"
              type="email"
              class="form-input"
              :placeholder="$t('common.email')"
            >
          </div>
          <p v-if="profileError" class="error-msg">{{ profileError }}</p>
          <p v-if="profileSuccess" class="success-msg">{{ profileSuccess }}</p>
          <button type="submit" class="btn-submit" :disabled="profileLoading">
            {{ profileLoading ? $t('common.saving') : $t('common.save') }}
          </button>
        </form>
      </section>

      <section class="password-section">
        <h2>{{ $t('profile.changePassword') }}</h2>
        <form @submit.prevent="handleChangePassword" class="profile-form">
          <div class="form-group">
            <label for="current">{{ $t('profile.currentPassword') }}</label>
            <input
              id="current"
              v-model="passwordForm.current_password"
              type="password"
              class="form-input"
              :placeholder="$t('profile.currentPassword')"
              required
            >
          </div>
          <div class="form-group">
            <label for="new">{{ $t('profile.newPassword') }}</label>
            <input
              id="new"
              v-model="passwordForm.new_password"
              type="password"
              class="form-input"
              :placeholder="$t('profile.newPasswordPlaceholder')"
              required
              minlength="6"
            >
          </div>
          <div class="form-group">
            <label for="confirm">{{ $t('profile.newPasswordConfirm') }}</label>
            <input
              id="confirm"
              v-model="passwordForm.new_password_confirm"
              type="password"
              class="form-input"
              :placeholder="$t('profile.newPasswordConfirmPlaceholder')"
              required
              minlength="6"
            >
          </div>
          <p v-if="error" class="error-msg">{{ error }}</p>
          <p v-if="success" class="success-msg">{{ success }}</p>
          <button type="submit" class="btn-submit" :disabled="loading">
            {{ loading ? $t('common.saving') : $t('profile.changePassword') }}
          </button>
        </form>
      </section>
    </div>
  </div>
</template>

<script>
const TOKEN_KEY = 'admin_token'

export default {
  name: 'Profile',
  data() {
    return {
      profile: null,
      profileForm: { name: '', email: '' },
      profileLoading: false,
      profileError: '',
      profileSuccess: '',
      passwordForm: {
        current_password: '',
        new_password: '',
        new_password_confirm: ''
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  mounted() {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      this.$router.replace('/login')
      return
    }
    this.loadProfile()
  },
  methods: {
    authHeaders() {
      const token = localStorage.getItem(TOKEN_KEY)
      return token ? { 'Authorization': 'Bearer ' + token } : {}
    },
    async loadProfile() {
      try {
        const r = await fetch('/v1/admin/profile', {
          headers: this.authHeaders()
        })
        if (!r.ok) {
          if (r.status === 401) this.$router.replace('/login')
          return
        }
        const data = await r.json()
        this.profile = data
        this.profileForm = { name: data.name || '', email: data.email || '' }
      } catch {
        this.profile = null
      }
    },
    async handleUpdateProfile() {
      this.profileError = ''
      this.profileSuccess = ''
      this.profileLoading = true
      try {
        const r = await fetch('/v1/admin/profile', {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            ...this.authHeaders()
          },
          body: JSON.stringify({
            name: this.profileForm.name.trim(),
            email: this.profileForm.email.trim() || null
          })
        })
        const data = await r.json().catch(() => ({}))
        if (!r.ok) {
          const msg = Array.isArray(data.detail) ? data.detail.map(d => d.msg).join(', ') : (data.detail || this.$t('profile.saveError'))
          throw new Error(msg)
        }
        this.profile = data
        this.profileForm = { name: data.name || '', email: data.email || '' }
        this.profileSuccess = this.$t('profile.saveSuccess')
      } catch (e) {
        this.profileError = e.message || this.$t('profile.saveError')
      } finally {
        this.profileLoading = false
      }
    },
    async handleChangePassword() {
      this.error = ''
      this.success = ''
      if (this.passwordForm.new_password !== this.passwordForm.new_password_confirm) {
        this.error = this.$t('profile.newPasswordMismatch')
        return
      }
      if (this.passwordForm.new_password.length < 6) {
        this.error = this.$t('profile.newPasswordMinLength')
        return
      }
      this.loading = true
      try {
        const r = await fetch('/v1/admin/profile/password', {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            ...this.authHeaders()
          },
          body: JSON.stringify({
            current_password: this.passwordForm.current_password,
            new_password: this.passwordForm.new_password,
            new_password_confirm: this.passwordForm.new_password_confirm
          })
        })
        const data = await r.json().catch(() => ({}))
        if (!r.ok) {
          const msg = Array.isArray(data.detail) ? data.detail.map(d => d.msg).join(', ') : (data.detail || this.$t('profile.passwordChangeError'))
          throw new Error(msg)
        }
        this.success = this.$t('profile.passwordChanged')
        this.passwordForm = { current_password: '', new_password: '', new_password_confirm: '' }
      } catch (e) {
        this.error = e.message || this.$t('profile.passwordChangeError')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.profile-page {
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2rem;
  background: var(--bg, #0f172a);
  color: #f1f5f9;
}
.profile-card {
  width: 100%;
  max-width: 420px;
  background: var(--surface, #1e293b);
  border-radius: 12px;
  padding: 2rem;
  border: 1px solid rgba(255,255,255,0.06);
}
.profile-card h1 { font-size: 1.5rem; margin: 0 0 0.5rem; color: #f1f5f9; }
.subtitle { color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem; }
.profile-section { margin-bottom: 1.5rem; }
.profile-section h2,
.password-section h2 { font-size: 1.1rem; color: #e2e8f0; margin: 0 0 1rem; }
.password-section { padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.06); }
.form-input-readonly { opacity: 0.7; cursor: not-allowed; }
.profile-form { display: flex; flex-direction: column; gap: 1.25rem; }
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
.success-msg { color: #34d399; font-size: 0.9rem; margin: 0; }
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
</style>
