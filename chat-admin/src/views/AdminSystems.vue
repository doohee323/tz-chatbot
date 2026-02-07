<template>
  <div class="admin-systems-page">
    <div class="admin-page">
    <div class="admin-header">
      <h1>{{ $t('systems.title') }}</h1>
      <div class="header-actions">
        <router-link to="/admin" class="nav-link">{{ $t('systems.chatList') }}</router-link>
        <button type="button" class="nav-link btn-sample-download" @click="downloadSampleZip">{{ $t('systems.sampleCode') }}</button>
        <button class="btn-add" @click="openForm()">{{ $t('systems.add') }}</button>
      </div>
    </div>

    <div v-if="showForm" class="form-page">
      <h2>{{ editing ? $t('systems.editSystem') : $t('systems.addSystem') }}</h2>
      <div class="form-card">
      <form @submit.prevent="save">
        <div class="form-row">
          <label>System ID</label>
          <input v-model="form.system_id" type="text" required :disabled="editing" placeholder="e.g. drillquiz" />
        </div>
        <div class="form-row">
          <label>{{ $t('systems.displayName') }}</label>
          <input v-model="form.display_name" type="text" placeholder="e.g. DrillQuiz" />
        </div>
        <div class="form-row">
          <label>Dify Base URL</label>
          <input v-model="form.dify_base_url" type="text" required placeholder="https://dify.drillquiz.com" />
        </div>
        <div class="form-row">
          <label>{{ $t('systems.difyApp') }}</label>
          <div class="form-field">
            <a :href="difyAppsUrl" target="_blank" rel="noopener noreferrer" class="dify-apps-link">
              {{ editing ? $t('systems.difyAppsCheck') : $t('systems.difyAppsCreate') }}
            </a>
            <span class="hint">{{ editing ? $t('systems.difyHintEdit') : $t('systems.difyHintCreate') }}</span>
            <span class="sample-link-wrap">
              <button type="button" class="btn-sample" @click="openSampleModal">{{ $t('systems.dslSample') }}</button>
            </span>
          </div>
        </div>
        <template v-if="editing">
          <div class="form-row">
            <label>Dify API Key</label>
            <input v-model="form.dify_api_key" type="password" required placeholder="app-xxx" />
          </div>
          <div class="form-row">
            <label>{{ $t('systems.difyChatbotToken') }}</label>
            <input v-model="form.dify_chatbot_token" type="password" :placeholder="$t('systems.difyChatbotTokenPlaceholder')" />
          </div>
        </template>
        <div class="form-row">
          <label>{{ $t('systems.allowedOrigins') }}</label>
          <textarea v-model="form.allowed_origins" placeholder="https://example.com,https://app.example.com" rows="3"></textarea>
        </div>
        <div class="form-row form-row-checkbox">
          <label><input v-model="form.enabled" type="checkbox" /> {{ $t('systems.active') }}</label>
        </div>
        <div v-if="editing" class="form-row rag-files-section">
          <label>{{ $t('systems.ragFiles') }} (rag-docs/raw/{{ editing.system_id }}/)</label>
          <div class="rag-files-list">
            <div v-if="ragFilesLoading" class="rag-loading">{{ $t('systems.loadingFiles') }}</div>
            <table v-else-if="ragFiles.length" class="rag-files-table">
              <thead>
                <tr><th>{{ $t('systems.filename') }}</th><th>{{ $t('systems.size') }}</th><th>{{ $t('systems.modified') }}</th><th></th></tr>
              </thead>
              <tbody>
                <tr v-for="f in ragFiles" :key="f.object_name">
                  <td>{{ f.filename }}</td>
                  <td>{{ formatSize(f.size) }}</td>
                  <td>{{ formatDate(f.last_modified) }}</td>
                  <td>
                    <button type="button" class="btn-del-small" @click="confirmDeleteRagFile(f)" :title="$t('common.delete')">{{ $t('common.delete') }}</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-else class="rag-empty">{{ $t('systems.noFiles') }}</p>
          </div>
          <div class="upload-controls">
            <input ref="fileInput" type="file" accept=".pdf,.txt,.md,.zip" @change="onFileSelect" style="display:none" />
            <button type="button" class="btn-upload" @click="$refs.fileInput?.click()">{{ $t('systems.selectFile') }}</button>
            <span v-if="uploadFile" class="upload-filename">{{ uploadFile.name }}</span>
            <button v-if="uploadFile" type="button" class="btn-do-upload" @click="doUpload" :disabled="uploading">
              {{ uploading ? $t('systems.uploading') : $t('systems.upload') }}
            </button>
          </div>
          <p class="hint">{{ $t('systems.uploadHint') }}</p>
          <p v-if="uploadResult" class="upload-result">{{ uploadResult }}</p>
          <div class="rag-table-actions">
            <button type="button" class="btn-reindex" @click="triggerReindex" :disabled="reindexing">
              {{ reindexing ? $t('systems.running') : $t('systems.ragRun') }}
            </button>
            <button type="button" class="btn-apply-settings" @click="applySettings" :disabled="applyingSettings">
              {{ applyingSettings ? $t('systems.applyingSettings') : $t('systems.applySettings') }}
            </button>
          </div>
        </div>
        <p v-if="formError" class="error">{{ formError }}</p>
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="closeForm">{{ $t('common.cancel') }}</button>
          <button type="submit" class="btn-save" :disabled="saving">{{ saving ? $t('common.saving') : $t('common.save') }}</button>
        </div>
      </form>
      </div>
    </div>

    <template v-else>
      <div class="systems-table-wrap">
      <table class="systems-table">
        <thead>
          <tr>
            <th>System ID</th>
            <th>{{ $t('systems.displayName') }}</th>
            <th>Dify URL</th>
            <th>Chatbot Token</th>
            <th>{{ $t('systems.active') }}</th>
            <th>{{ $t('systems.manage') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in systems" :key="s.system_id">
            <td>{{ s.system_id }}</td>
            <td>{{ s.display_name || '-' }}</td>
            <td class="url-cell">{{ s.dify_base_url || '-' }}</td>
            <td class="key-cell">{{ maskKey(s.dify_chatbot_token) }}</td>
            <td>{{ s.enabled ? 'Y' : 'N' }}</td>
            <td>
              <button class="btn-test" @click="openTestChat(s)">{{ $t('common.test') }}</button>
              <button class="btn-edit" @click="openForm(s)">{{ $t('common.edit') }}</button>
              <button class="btn-del" @click="confirmDelete(s)">{{ $t('common.delete') }}</button>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
      <p v-if="!loading && systems.length === 0" class="empty">{{ $t('systems.noSystems') }}</p>
    </template>

    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal">
        <h3>{{ $t('systems.confirmDelete') }}</h3>
        <p>{{ deleteTarget.system_id }}{{ $t('systems.deleteSystemConfirm') }}</p>
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="deleteTarget = null">{{ $t('common.cancel') }}</button>
          <button type="button" class="btn-del" @click="doDelete" :disabled="deleting">{{ deleting ? $t('common.deleting') : $t('common.delete') }}</button>
        </div>
      </div>
    </div>

    <div v-if="deleteRagTarget" class="modal-overlay" @click.self="deleteRagTarget = null">
      <div class="modal">
        <h3>{{ $t('systems.deleteRagFile') }}</h3>
        <p>{{ $t('systems.deleteRagConfirm', { filename: deleteRagTarget?.filename }) }}</p>
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="deleteRagTarget = null">{{ $t('common.cancel') }}</button>
          <button type="button" class="btn-del" @click="doDeleteRagFile" :disabled="deletingRag">{{ deletingRag ? $t('common.deleting') : $t('common.delete') }}</button>
        </div>
      </div>
    </div>

    <div v-if="showSampleModal" class="modal-overlay" @click.self="showSampleModal = false">
      <div class="modal modal-sample">
        <h3>{{ $t('systems.sampleYamlTitle') }}</h3>
        <p class="sample-hint">{{ $t('systems.sampleYamlHint') }}</p>
        <pre class="sample-code">{{ sampleYaml }}</pre>
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="showSampleModal = false">{{ $t('common.close') }}</button>
        </div>
      </div>
    </div>

    <div v-if="applyingSettings" class="modal-overlay applying-overlay">
      <div class="applying-panel">
        <div class="spinner"></div>
        <p class="applying-text">{{ $t('systems.restarting') }}</p>
        <p class="applying-hint">{{ $t('systems.restartHint') }}</p>
      </div>
    </div>

    <div v-if="showTestChat" class="modal-overlay" @click.self="closeTestChat">
      <div class="modal modal-chat">
        <div class="modal-chat-header">
          <h3>{{ $t('systems.chatTest') }} — {{ testChatSystemId }}</h3>
          <button type="button" class="btn-close" @click="closeTestChat">{{ $t('common.close') }}</button>
        </div>
        <div class="modal-chat-body" v-if="testChatToken">
          <Chat
            :chat-token="testChatToken"
            :chat-system-id="testChatSystemId"
            :chat-user-id="testChatUserId"
            in-modal
          />
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import Chat from './Chat.vue'

const TOKEN_KEY = 'admin_token'
const API = '/v1/admin/systems'

export default {
  name: 'AdminSystems',
  components: { Chat },
  data() {
    return {
      systems: [],
      loading: false,
      showForm: false,
      editing: null,
      form: {
        system_id: '',
        display_name: '',
        dify_base_url: '',
        dify_api_key: '',
        dify_chatbot_token: '',
        allowed_origins: '',
        enabled: true
      },
      formError: '',
      saving: false,
      deleteTarget: null,
      deleting: false,
      showTestChat: false,
      testChatToken: '',
      testChatSystemId: '',
      testChatUserId: '',
      uploadFile: null,
      uploading: false,
      uploadResult: '',
      ragFiles: [],
      ragFilesLoading: false,
      deleteRagTarget: null,
      deletingRag: false,
      reindexing: false,
      applyingSettings: false,
      showSampleModal: false,
      sampleYaml: ''
    }
  },
  computed: {
    difyAppsUrl() {
      const base = (this.form.dify_base_url || 'https://dify.drillquiz.com').trim().replace(/\/$/, '')
      return base + '/apps'
    }
  },
  mounted() {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      this.$router.replace('/login')
      return
    }
    this.load()
  },
  methods: {
    authHeaders() {
      const token = localStorage.getItem(TOKEN_KEY)
      return token ? { 'Authorization': 'Bearer ' + token } : {}
    },
    async load() {
      this.loading = true
      try {
        const r = await fetch(API, { headers: this.authHeaders() })
        if (r.status === 401) {
          localStorage.removeItem(TOKEN_KEY)
          this.$router.replace('/login')
          return
        }
        if (!r.ok) throw new Error(await r.text())
        this.systems = await r.json()
      } catch (e) {
        this.formError = e.message
      } finally {
        this.loading = false
      }
    },
    maskKey(k) {
      if (!k) return '-'
      if (k.length <= 8) return '***'
      return k.slice(0, 4) + '...' + k.slice(-4)
    },
    async openTestChat(s) {
      this.formError = ''
      try {
        const r = await fetch(API + '/' + encodeURIComponent(s.system_id) + '/test-token', {
          headers: this.authHeaders()
        })
        if (r.status === 401) {
          localStorage.removeItem(TOKEN_KEY)
          this.$router.replace('/login')
          return
        }
        if (!r.ok) {
          const d = await r.json().catch(() => ({}))
          throw new Error(d.detail || 'Token issuance failed')
        }
        const { token } = await r.json()
        this.testChatToken = token
        this.testChatSystemId = s.system_id
        this.testChatUserId = 'admin_test'
        this.showTestChat = true
      } catch (e) {
        this.formError = e.message
      }
    },
    async downloadSampleZip() {
      this.formError = ''
      try {
        const r = await fetch('/v1/admin/sample/download', { headers: this.authHeaders() })
        if (r.status === 401) {
          localStorage.removeItem(TOKEN_KEY)
          this.$router.replace('/login')
          return
        }
        if (!r.ok) throw new Error('Download failed')
        const blob = await r.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'chat-admin-sample.zip'
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        this.formError = e.message
      }
    },
    async openSampleModal() {
      this.showSampleModal = true
      if (!this.sampleYaml) {
        try {
          const r = await fetch('/drillquiz-rag-openapi.yaml')
          if (r.ok) this.sampleYaml = await r.text()
          else this.sampleYaml = '# Load failed'
        } catch {
          this.sampleYaml = '# Load failed'
        }
      }
    },
    closeTestChat() {
      this.showTestChat = false
      this.testChatToken = ''
      this.testChatSystemId = ''
      this.testChatUserId = ''
    },
    async openForm(s) {
      this.editing = s || null
      this.formError = ''
      if (s) {
        this.form = {
          system_id: s.system_id,
          display_name: s.display_name || '',
          dify_base_url: s.dify_base_url || '',
          dify_api_key: s.dify_api_key || '',
          dify_chatbot_token: s.dify_chatbot_token || '',
          allowed_origins: s.allowed_origins || '',
          enabled: s.enabled
        }
        this.showForm = true
        await this.loadRagFiles()
      } else {
        this.form = {
          system_id: '',
          display_name: '',
          dify_base_url: 'https://dify.drillquiz.com',
          dify_api_key: '',
          dify_chatbot_token: '',
          allowed_origins: '',
          enabled: true
        }
        this.showForm = true
      }
    },
    closeForm() {
      this.showForm = false
      this.editing = null
      this.uploadFile = null
      this.uploadResult = ''
      this.ragFiles = []
      this.deleteRagTarget = null
    },
    formatSize(n) {
      if (!n || n < 1024) return (n || 0) + ' B'
      if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB'
      return (n / (1024 * 1024)).toFixed(1) + ' MB'
    },
    formatDate(s) {
      if (!s) return '-'
      try {
        const d = new Date(s)
        return isNaN(d.getTime()) ? s : d.toLocaleString()
      } catch {
        return s
      }
    },
    async loadRagFiles() {
      if (!this.editing) return
      this.ragFilesLoading = true
      try {
        const r = await fetch(API + '/' + encodeURIComponent(this.editing.system_id) + '/files', {
          headers: this.authHeaders()
        })
        if (r.ok) this.ragFiles = await r.json()
        else this.ragFiles = []
      } catch {
        this.ragFiles = []
      } finally {
        this.ragFilesLoading = false
      }
    },
    confirmDeleteRagFile(f) {
      this.deleteRagTarget = f
      this.deletingRag = false
    },
    async triggerReindex() {
      if (!this.editing) return
      this.reindexing = true
      this.formError = ''
      try {
        const r = await fetch(API + '/' + encodeURIComponent(this.editing.system_id) + '/trigger-reindex', {
          method: 'POST',
          headers: this.authHeaders()
        })
        if (r.status === 401) {
          localStorage.removeItem(TOKEN_KEY)
          this.$router.replace('/login')
          return
        }
        if (!r.ok) {
          const d = await r.json().catch(() => ({}))
          throw new Error(d.detail || 'Indexing failed')
        }
        const d = await r.json()
        this.formError = ''
        this.uploadResult = `Job started: ${d.job_name || ''}`
      } catch (e) {
        this.formError = e.message
      } finally {
        this.reindexing = false
      }
    },
    async applySettings() {
      this.applyingSettings = true
      this.formError = ''
      try {
        const r = await fetch(API + '/apply-settings', {
          method: 'POST',
          headers: this.authHeaders()
        })
        if (r.status === 401) {
          localStorage.removeItem(TOKEN_KEY)
          this.$router.replace('/login')
          return
        }
        if (!r.ok) {
          const d = await r.json().catch(() => ({}))
          throw new Error(d.detail || 'Apply settings failed')
        }
        window.location.reload()
      } catch (e) {
        this.formError = e.message
      } finally {
        this.applyingSettings = false
      }
    },
    async doDeleteRagFile() {
      if (!this.deleteRagTarget || !this.editing) return
      this.deletingRag = true
      try {
        const r = await fetch(
          API + '/' + encodeURIComponent(this.editing.system_id) + '/files?key=' + encodeURIComponent(this.deleteRagTarget.object_name),
          { method: 'DELETE', headers: this.authHeaders() }
        )
        if (r.status === 401) {
          localStorage.removeItem(TOKEN_KEY)
          this.$router.replace('/login')
          return
        }
        if (!r.ok) throw new Error(await r.text())
        this.deleteRagTarget = null
        await this.loadRagFiles()
      } catch (e) {
        this.formError = e.message
      } finally {
        this.deletingRag = false
      }
    },
    onFileSelect(e) {
      const f = e.target?.files?.[0]
      this.uploadFile = f || null
      this.uploadResult = ''
    },
    async doUpload() {
      if (!this.editing || !this.uploadFile) return
      this.uploading = true
      this.formError = ''
      this.uploadResult = ''
      try {
        const formData = new FormData()
        formData.append('file', this.uploadFile)
        const r = await fetch(API + '/' + encodeURIComponent(this.editing.system_id) + '/upload', {
          method: 'POST',
          headers: this.authHeaders(),
          body: formData
        })
        if (r.status === 401) {
          localStorage.removeItem(TOKEN_KEY)
          this.$router.replace('/login')
          return
        }
        if (!r.ok) {
          const d = await r.json().catch(() => ({}))
          throw new Error(d.detail || 'Upload failed')
        }
        const d = await r.json()
        this.uploadResult = `${d.count} file(s) uploaded: ${d.uploaded?.join(', ') || ''}`
        this.uploadFile = null
        if (this.$refs.fileInput) this.$refs.fileInput.value = ''
        await this.loadRagFiles()
      } catch (e) {
        this.formError = e.message
      } finally {
        this.uploading = false
      }
    },
    async save() {
      this.formError = ''
      this.saving = true
      try {
        if (this.editing) {
          const r = await fetch(API + '/' + encodeURIComponent(this.editing.system_id), {
            method: 'PATCH',
            headers: { ...this.authHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify({
              display_name: this.form.display_name,
              dify_base_url: this.form.dify_base_url,
              dify_api_key: this.form.dify_api_key,
              dify_chatbot_token: this.form.dify_chatbot_token,
              allowed_origins: this.form.allowed_origins,
              enabled: this.form.enabled
            })
          })
          if (r.status === 401) {
            localStorage.removeItem(TOKEN_KEY)
            this.$router.replace('/login')
            return
          }
          if (!r.ok) {
            const d = await r.json().catch(() => ({}))
            throw new Error(d.detail || 'Update failed')
          }
        } else {
          const r = await fetch(API, {
            method: 'POST',
            headers: { ...this.authHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify(this.form)
          })
          if (r.status === 401) {
            localStorage.removeItem(TOKEN_KEY)
            this.$router.replace('/login')
            return
          }
          if (!r.ok) {
            const d = await r.json().catch(() => ({}))
            throw new Error(d.detail || 'Add failed')
          }
        }
        this.closeForm()
        await this.load()
      } catch (e) {
        this.formError = e.message
      } finally {
        this.saving = false
      }
    },
    confirmDelete(s) {
      this.deleteTarget = s
      this.deleting = false
    },
    async doDelete() {
      if (!this.deleteTarget) return
      this.deleting = true
      try {
        const r = await fetch(API + '/' + encodeURIComponent(this.deleteTarget.system_id), {
          method: 'DELETE',
          headers: this.authHeaders()
        })
        if (r.status === 401) {
          localStorage.removeItem(TOKEN_KEY)
          this.$router.replace('/login')
          return
        }
        if (!r.ok) throw new Error(await r.text())
        this.deleteTarget = null
        await this.load()
      } catch (e) {
        this.formError = e.message
      } finally {
        this.deleting = false
      }
    },
  }
}
</script>

<style scoped>
/* tz-cointutor style - variables */
.admin-systems-page {
  --primary: #6366f1;
  --secondary: #8b5cf6;
  --dark: #0f172a;
  --dark-light: #1e293b;
  --border: rgba(255, 255, 255, 0.1);
  --border-20: rgba(255, 255, 255, 0.2);
  background: linear-gradient(to bottom right, var(--dark), var(--dark-light), var(--dark));
  min-height: calc(100vh - 56px);
  color: #fff;
}
.admin-page { padding: 1.5rem 1rem; max-width: 80rem; margin: 0 auto; }
.admin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.75rem; }
.admin-header h1 { margin: 0; font-size: 1.5rem; font-weight: 700; }
.header-actions { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.nav-link { padding: 0.5rem 1rem; background: transparent; color: #9ca3af; text-decoration: none; border-radius: 0.75rem; font-size: 0.9rem; border: 1px solid var(--border-20); transition: all 0.2s; }
.nav-link:hover { color: var(--primary); border-color: rgba(99, 102, 241, 0.5); }
.btn-sample-download { border: 1px solid var(--border-20); cursor: pointer; font: inherit; background: transparent; color: #9ca3af; padding: 0.5rem 1rem; border-radius: 0.75rem; transition: all 0.2s; }
.btn-sample-download:hover { color: var(--primary); border-color: rgba(99, 102, 241, 0.5); }
.btn-add { padding: 0.5rem 1rem; background: linear-gradient(to right, var(--primary), var(--secondary)); color: #fff; border: none; border-radius: 0.75rem; cursor: pointer; font-weight: 600; transition: box-shadow 0.2s; }
.btn-add:hover { box-shadow: 0 10px 20px rgba(99, 102, 241, 0.4); }
.systems-table-wrap { background: linear-gradient(to bottom right, var(--dark-light), var(--dark)); border: 1px solid var(--border); border-radius: 1rem; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); }
.systems-table { border-collapse: collapse; width: 100%; }
.systems-table th, .systems-table td { padding: 0.75rem 1rem; text-align: left; }
.systems-table thead { background: rgba(15, 23, 42, 0.5); }
.systems-table th { font-size: 0.875rem; font-weight: 600; color: #d1d5db; }
.systems-table tbody tr { border-top: 1px solid var(--border); transition: background 0.2s; }
.systems-table tbody tr:hover { background: rgba(15, 23, 42, 0.5); }
.url-cell { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.key-cell { font-family: monospace; font-size: 0.85em; }
.btn-test { padding: 0.25rem 0.5rem; background: rgba(99, 102, 241, 0.2); color: var(--primary); border: none; border-radius: 0.5rem; cursor: pointer; margin-right: 0.25rem; font-size: 0.875rem; font-weight: 500; }
.btn-test:hover { background: rgba(99, 102, 241, 0.3); }
.btn-edit { padding: 0.25rem 0.5rem; background: rgba(139, 92, 246, 0.2); color: var(--secondary); border: none; border-radius: 0.5rem; cursor: pointer; margin-right: 0.25rem; font-size: 0.875rem; font-weight: 500; }
.btn-edit:hover { background: rgba(139, 92, 246, 0.3); }
.btn-del { padding: 0.25rem 0.5rem; background: rgba(239, 68, 68, 0.2); color: #f87171; border: none; border-radius: 0.5rem; cursor: pointer; font-size: 0.875rem; font-weight: 500; }
.btn-del:hover { background: rgba(239, 68, 68, 0.3); }
.empty { color: #9ca3af; padding: 2rem; text-align: center; }
.form-page { max-width: 56rem; }
.form-page .form-card { background: linear-gradient(to bottom right, var(--dark-light), var(--dark)); border: 1px solid var(--border); border-radius: 1rem; padding: 1.5rem 2rem; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); }
.form-page h2 { margin: 0 0 1.5rem; font-size: 1.5rem; font-weight: 700; }
.form-row { margin-bottom: 1.5rem; display: flex; align-items: flex-start; gap: 1rem; }
.form-row label { flex-shrink: 0; width: 10rem; padding-top: 0.75rem; font-size: 0.875rem; font-weight: 600; color: #d1d5db; }
.form-row input:not([type="checkbox"]),
.form-row textarea { flex: 1; min-width: 12rem; padding: 0.75rem 1rem; border: 1px solid var(--border-20); border-radius: 0.75rem; background: var(--dark); color: #fff; font-size: 0.95rem; transition: border-color 0.2s; box-sizing: border-box; -webkit-appearance: none; appearance: none; }
.form-row input::placeholder,
.form-row textarea::placeholder { color: rgba(255, 255, 255, 0.5); }
.form-row textarea { min-height: 4rem; resize: vertical; }
.form-field { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.25rem; }
.form-row input:focus { outline: none; border-color: var(--primary); }
.form-row input:disabled { opacity: 0.6; }
.form-row input[type="checkbox"] { margin-right: 0.5rem; }
.form-row.rag-files-section { flex-direction: column; }
.form-row.rag-files-section > label { width: auto; padding-top: 0; margin-bottom: 0.5rem; }
.form-row-checkbox { align-items: center; }
.form-row-checkbox > label { width: auto; padding-top: 0; flex: 1; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.75); display: flex; align-items: center; justify-content: center; z-index: 1040; padding: 1rem; }
.modal { background: linear-gradient(to bottom right, var(--dark-light), var(--dark)); border: 1px solid var(--border); border-radius: 1rem; padding: 1.5rem; min-width: 400px; max-width: 90vw; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); }
.modal h3 { margin: 0 0 1rem; color: #fff; font-weight: 600; }
.modal p { color: #e5e7eb; }
.rag-files-section .rag-files-list { margin-bottom: 0.75rem; overflow-x: auto; }
.rag-files-section .rag-loading, .rag-files-section .rag-empty { font-size: 0.9rem; color: #6b7280; }
.rag-files-table { width: 100%; min-width: 640px; border-collapse: collapse; font-size: 0.9rem; }
.rag-files-table th, .rag-files-table td { padding: 0.5rem 0.75rem; text-align: left; border: 1px solid var(--border); }
.rag-files-table th { background: rgba(15, 23, 42, 0.5); color: #9ca3af; }
.btn-del-small { padding: 0.2rem 0.5rem; font-size: 0.8rem; background: rgba(239, 68, 68, 0.2); color: #f87171; border: none; border-radius: 0.5rem; cursor: pointer; }
.btn-del-small:hover { background: rgba(239, 68, 68, 0.3); }
.rag-table-actions { margin-bottom: 0.75rem; display: flex; gap: 0.5rem; flex-wrap: wrap; }
.btn-reindex { padding: 0.5rem 1rem; background: rgba(99, 102, 241, 0.2); color: #fff; border: none; border-radius: 0.75rem; cursor: pointer; font-weight: 500; }
.btn-reindex:hover:not(:disabled) { background: rgba(99, 102, 241, 0.3); }
.btn-reindex:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-apply-settings { padding: 0.5rem 1rem; background: rgba(34, 197, 94, 0.2); color: #4ade80; border: none; border-radius: 0.75rem; cursor: pointer; font-weight: 500; }
.btn-apply-settings:hover:not(:disabled) { background: rgba(34, 197, 94, 0.3); }
.btn-apply-settings:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-apply-settings-header { padding: 0.5rem 1rem; background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); border-radius: 0.75rem; cursor: pointer; font-weight: 500; font-size: 0.9rem; }
.btn-apply-settings-header:hover:not(:disabled) { background: rgba(34, 197, 94, 0.3); }
.btn-apply-settings-header:disabled { opacity: 0.6; cursor: not-allowed; }
.applying-overlay { pointer-events: all; }
.applying-panel { background: linear-gradient(to bottom right, var(--dark-light), var(--dark)); border: 1px solid var(--border); border-radius: 1rem; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 1rem; min-width: 280px; }
.applying-text { margin: 0; color: #fff; font-weight: 600; }
.applying-hint { margin: 0; color: #9ca3af; font-size: 0.9rem; }
.spinner { width: 40px; height: 40px; border: 3px solid rgba(255, 255, 255, 0.2); border-top-color: var(--primary); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.rag-files-section .upload-controls { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.upload-filename { font-size: 0.9rem; color: #9ca3af; }
.btn-upload, .btn-do-upload { padding: 0.5rem 1rem; background: rgba(15, 23, 42, 0.6); color: #9ca3af; border: 1px solid var(--border); border-radius: 0.75rem; cursor: pointer; }
.btn-upload:hover, .btn-do-upload:hover { background: rgba(30, 41, 59, 0.8); color: #fff; }
.btn-do-upload { background: rgba(99, 102, 241, 0.2); color: var(--primary); }
.btn-do-upload:hover:not(:disabled) { background: rgba(99, 102, 241, 0.3); }
.btn-do-upload:disabled { opacity: 0.6; cursor: not-allowed; }
.upload-result { font-size: 0.85rem; color: #4ade80; margin-top: 0.5rem; }
.hint { font-size: 0.8rem; color: #6b7280; margin-left: 0; margin-top: 0.25rem; display: block; }
.dify-apps-link { color: var(--primary); text-decoration: none; }
.dify-apps-link:hover { text-decoration: underline; }
.form-actions { display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: 1.5rem; }
.btn-cancel { padding: 0.5rem 1rem; border: 2px solid var(--border-20); background: transparent; color: #e5e7eb; border-radius: 0.75rem; cursor: pointer; font-weight: 500; }
.btn-cancel:hover { background: rgba(255, 255, 255, 0.05); }
.btn-save { padding: 0.5rem 1rem; background: linear-gradient(to right, var(--primary), var(--secondary)); color: #fff; border: none; border-radius: 0.75rem; cursor: pointer; font-weight: 600; }
.btn-save:hover:not(:disabled) { box-shadow: 0 10px 20px rgba(99, 102, 241, 0.4); }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }
.error { color: #f87171; font-size: 0.9rem; }
.modal-chat { min-width: 600px; max-width: 95vw; width: 800px; padding: 0; overflow: hidden; display: flex; flex-direction: column; max-height: 85vh; }
.modal-chat-header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; border-bottom: 1px solid var(--border); }
.modal-chat-header h3 { margin: 0; font-size: 1rem; color: #fff; }
.btn-close { padding: 0.5rem 1rem; background: rgba(100, 116, 139, 0.3); color: #fff; border: none; border-radius: 0.75rem; cursor: pointer; }
.btn-close:hover { background: rgba(100, 116, 139, 0.5); }
.modal-chat-body { flex: 1; min-height: 0; overflow: hidden; background: #fff; }
.modal-sample { max-width: 700px; max-height: 80vh; overflow: hidden; display: flex; flex-direction: column; }
.modal-sample h3 { margin: 0 0 0.5rem; }
.sample-hint { font-size: 0.85rem; color: #9ca3af; margin: 0 0 0.5rem; }
.sample-code { flex: 1; overflow: auto; background: var(--dark); padding: 1rem; border-radius: 0.75rem; font-size: 0.8rem; line-height: 1.4; color: #e2e8f0; margin: 0; white-space: pre-wrap; word-break: break-all; }
.sample-link-wrap { display: block; margin-top: 0.5rem; }
.btn-sample { padding: 0.25rem 0.5rem; font-size: 0.85rem; background: rgba(15, 23, 42, 0.6); color: #9ca3af; border: 1px solid var(--border-20); border-radius: 0.5rem; cursor: pointer; }
.btn-sample:hover { background: rgba(30, 41, 59, 0.8); color: #fff; }
</style>
