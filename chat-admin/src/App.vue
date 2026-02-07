<template>
  <div id="app">
    <header class="app-header">
      <div class="nav-left">
        <router-link to="/" class="logo">{{ $t('menu.appName') }}</router-link>
        <template v-if="isAdminArea">
          <router-link to="/admin/systems" class="nav-link">{{ $t('menu.chatManage') }}</router-link>
          <router-link to="/admin" class="nav-link">{{ $t('menu.chatList') }}</router-link>
        </template>
      </div>
      <nav class="nav-right">
        <div class="lang-dropdown">
          <button type="button" class="btn-lang" @click="showLangMenu = !showLangMenu">
            <span>{{ currentLangLabel }}</span>
            <svg class="chevron-icon" viewBox="0 0 320 512" width="10" height="10" fill="currentColor">
              <path d="M137.4 374.6c12.5 12.5 32.8 12.5 45.3 0l128-128c9.2-9.2 11.9-22.9 6.9-34.9s-16.6-19.8-29.6-19.8L32 192c-12.9 0-24.6 7.8-29.6 19.8s-2.2 25.7 6.9 34.9l128 128z"/>
            </svg>
          </button>
          <div v-if="showLangMenu" class="lang-menu" @click="showLangMenu = false">
            <a href="#" @click.prevent="$changeLanguage('ko')">한국어</a>
            <a href="#" @click.prevent="$changeLanguage('en')">English</a>
          </div>
        </div>
        <template v-if="isAdminArea && adminUsername">
          <div class="user-dropdown">
            <button
              type="button"
              class="btn-user"
              @click="showUserMenu = !showUserMenu"
            >
              <span>{{ adminUsername }}</span>
              <svg class="chevron-icon" viewBox="0 0 320 512" width="10" height="10" fill="currentColor">
                <path d="M137.4 374.6c12.5 12.5 32.8 12.5 45.3 0l128-128c9.2-9.2 11.9-22.9 6.9-34.9s-16.6-19.8-29.6-19.8L32 192c-12.9 0-24.6 7.8-29.6 19.8s-2.2 25.7 6.9 34.9l128 128z"/>
              </svg>
            </button>
            <div
              v-if="showUserMenu"
              class="user-menu"
              @mouseleave="showUserMenu = false"
              @click="showUserMenu = false"
            >
              <router-link to="/admin/profile" class="user-menu-item">
                {{ $t('profile.title') }}
              </router-link>
              <a href="#" class="user-menu-item user-menu-logout" @click.prevent="logout">
                {{ $t('menu.logout') }}
              </a>
            </div>
          </div>
        </template>
        <template v-else>
          <router-link to="/about" class="nav-link">{{ $t('menu.about') }}</router-link>
          <router-link to="/login" class="nav-link">{{ $t('menu.login') }}</router-link>
        </template>
      </nav>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script>
const TOKEN_KEY = 'admin_token'

function parseUsernameFromToken(token) {
  if (!token) return null
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
    return payload.sub || null
  } catch {
    return null
  }
}

export default {
  name: 'App',
  data() {
    return {
      showLangMenu: false,
      showUserMenu: false
    }
  },
  computed: {
    currentLangLabel() {
      const langMap = { ko: '🇰🇷 KO', en: '🇺🇸 EN' }
      return langMap[this.$i18n.locale] || '🇺🇸 EN'
    },
    isAdminArea() {
      return this.$route.path.startsWith('/admin')
    },
    adminUsername() {
      this.$route.path // re-evaluate when route changes (e.g. after login)
      return parseUsernameFromToken(localStorage.getItem(TOKEN_KEY))
    }
  },
  methods: {
    logout() {
      localStorage.removeItem(TOKEN_KEY)
      this.$router.replace('/login')
    }
  }
}
</script>

<style>
* { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, sans-serif; background: #0f172a; }
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: var(--bg, #0f172a);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  z-index: 100;
}
.app-header .logo {
  font-size: 1.1rem;
  font-weight: 700;
  color: #f1f5f9;
  text-decoration: none;
}
.app-header .logo:hover { color: #38bdf8; }
.nav-left { display: flex; align-items: center; gap: 1rem; }
.nav-right { display: flex; align-items: center; gap: 1rem; }
.user-dropdown { position: relative; }
.btn-user {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0.4rem 0.75rem;
  background: transparent;
  color: #94a3b8;
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
}
.btn-user:hover { color: #38bdf8; background: rgba(56, 189, 248, 0.1); }
.btn-user .chevron-icon { flex-shrink: 0; opacity: 0.85; }
.user-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  min-width: 140px;
  background: #1e293b;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 4px;
  z-index: 50;
}
.user-menu-item {
  display: block;
  padding: 8px 12px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.9rem;
  border-radius: 4px;
}
.user-menu-item:hover { color: #fff; background: rgba(56, 189, 248, 0.2); }
.user-menu-logout { color: #94a3b8; }
.user-menu-logout:hover { color: #f87171; background: rgba(248, 113, 113, 0.15); }
.nav-link {
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.95rem;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  border: 1px solid rgba(56, 189, 248, 0.25);
}
.nav-link:hover { color: #38bdf8; background: rgba(56, 189, 248, 0.1); }
.lang-dropdown { position: relative; }
.btn-lang {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0.4rem 0.75rem;
  background: transparent;
  color: #94a3b8;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-lang .chevron-icon { flex-shrink: 0; opacity: 0.85; }
.btn-lang:hover { color: #fff; background: rgba(255,255,255,0.05); }
.lang-menu { position: absolute; top: 100%; right: 0; margin-top: 4px; min-width: 120px; background: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 4px; z-index: 50; }
.lang-menu a { display: block; padding: 8px 12px; color: #94a3b8; text-decoration: none; font-size: 0.9rem; border-radius: 4px; }
.lang-menu a:hover { color: #fff; background: rgba(56, 189, 248, 0.2); }
.app-main { padding-top: 56px; min-height: 100vh; background: #0f172a; }
</style>
