import Vue from 'vue'
import VueI18n from 'vue-i18n'
import ko from './locales/ko'
import en from './locales/en'

Vue.use(VueI18n)

function detectBrowserLanguage() {
  const browser = (navigator.language || navigator.userLanguage || 'en').toLowerCase()
  return browser.startsWith('ko') ? 'ko' : 'en'
}

const i18n = new VueI18n({
  locale: detectBrowserLanguage(),
  fallbackLocale: 'en',
  messages: {
    ko,
    en
  },
  silentTranslationWarn: process.env.NODE_ENV === 'production',
  missing: (locale, key) => key
})

function changeLanguage(language) {
  if (['ko', 'en'].includes(language)) {
    i18n.locale = language
    localStorage.setItem('language', language)
    return true
  }
  return false
}

function initLanguage() {
  const saved = localStorage.getItem('language')
  const lang = saved || detectBrowserLanguage()
  changeLanguage(lang)
}

initLanguage()

Vue.prototype.$changeLanguage = changeLanguage

export default i18n
