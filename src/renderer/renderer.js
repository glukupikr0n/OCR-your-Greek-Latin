'use strict'

import { FilePanel } from './components/file-panel.js'
import { OptionsPanel } from './components/options-panel.js'
import { ProgressPanel } from './components/progress-panel.js'
import { PreviewPanel } from './components/preview-panel.js'
import { TOCPanel } from './components/toc-panel.js'
import { t, setLang, getLang, applyI18n } from './i18n.js'

const app = window.ocrApp

// Panels
const filePanel    = new FilePanel(app)
const optionsPanel = new OptionsPanel()
const progressPanel = new ProgressPanel()
const previewPanel  = new PreviewPanel()
const tocPanel      = new TOCPanel()

// Apply Korean as default language
applyI18n()

// Log helpers
function appendLog (msg, level = 'info') {
  const el = document.getElementById('log-output')
  if (!el) return
  const line = document.createElement('div')
  line.className = `log-line log-${level}`
  const ts = new Date().toLocaleTimeString()
  line.textContent = `[${ts}] ${msg}`
  el.appendChild(line)
  el.scrollTop = el.scrollHeight
}

let _currentJobId = null

// Language toggle
document.getElementById('btn-lang-toggle').addEventListener('click', () => {
  const next = getLang() === 'ko' ? 'en' : 'ko'
  setLang(next)
  applyI18n()
  // Update toggle button label
  document.getElementById('btn-lang-toggle').textContent = t('lang-toggle')
})

// File loaded → enable process
filePanel.onFileLoaded = async (filePath, totalPages) => {
  document.getElementById('btn-process').disabled = false
  previewPanel.setFile(filePath, totalPages)
  await previewPanel.showPage(0)
}

// Process button
document.getElementById('btn-process').addEventListener('click', async () => {
  const filePath = filePanel.getCurrentFile()
  if (!filePath) return

  const outputPath = await app.saveFileDialog({
    defaultPath: filePath.replace(/\.pdf$/i, '_searchable.pdf'),
    title: t('btn-process')
  })
  if (!outputPath) return

  const options = optionsPanel.getOptions()
  _currentJobId = crypto.randomUUID()

  document.getElementById('btn-process').classList.add('hidden')
  document.getElementById('btn-cancel').classList.remove('hidden')
  progressPanel.start(previewPanel.totalPages)
  appendLog(`Processing started (job ${_currentJobId.slice(0, 8)}…)`)

  const progressHandler = (data) => {
    progressPanel.update(data)
    appendLog(`Page ${data.page + 1}/${data.total_pages} — confidence ${data.current_word_confidence?.toFixed(1)}%`)
  }
  app.onProgress(progressHandler)

  try {
    const pageRange = options.pageRangeEnabled
      ? [options.pageRangeStart - 1, options.pageRangeEnd != null ? options.pageRangeEnd - 1 : null]
      : [0, null]

    const result = await app.processFile({
      input_path: filePath,
      output_path: outputPath,
      job_id: _currentJobId,
      languages: options.languages,
      options: {
        enhancement: options.enhancement,
        confidence_retry: options.confidenceRetry,
        confidence_threshold: options.confidenceThreshold,
        layout_detection: options.layoutDetection,
        toc_detection: options.tocDetection,
        page_numbering: options.pageNumbering,
        split_bilingual: options.splitBilingual,
        split_lang_a: options.splitLangA,
        split_lang_b: options.splitLangB,
        split_shared_start: options.splitSharedStart,
        split_shared_end: options.splitSharedEnd,
        page_range: pageRange,
        parallel_threads: options.threads
      }
    })

    if (result.status === 'cancelled') {
      appendLog('Processing cancelled.', 'warn')
    } else {
      appendLog(`Done — ${result.pages_processed} pages, avg confidence ${result.avg_confidence?.toFixed(1)}%`, 'success')
      progressPanel.finish(result)
      showResults(result)
      if (result.toc_entries?.length > 0) tocPanel.render(result.toc_entries)
    }

  } catch (err) {
    progressPanel.showError(err.message)
    appendLog(`Error: ${err.message}`, 'error')
  } finally {
    app.offProgress(progressHandler)
    _currentJobId = null
    document.getElementById('btn-cancel').classList.add('hidden')
    document.getElementById('btn-process').classList.remove('hidden')
  }
})

// Cancel
document.getElementById('btn-cancel').addEventListener('click', async () => {
  appendLog('Cancel requested…', 'warn')
  await app.cancelJob({ job_id: _currentJobId })
  progressPanel.showCancelled()
})

// Menu commands
app.onMenuCommand((cmd) => {
  if (cmd === 'menu:open-file') filePanel.onSelectFile()
  if (cmd === 'menu:process')   document.getElementById('btn-process').click()
  if (cmd === 'menu:cancel')    document.getElementById('btn-cancel').click()
})

// System ready / error
app.onSystemReady((info) => {
  if (!info.ready) {
    const missing = info.languages?.missing?.join(', ') || ''
    showBanner(t('system-missing-langs', { langs: missing }), 'warning')
    appendLog(`Warning: missing language data — ${missing}`, 'warn')
  } else {
    appendLog('Backend ready.', 'success')
  }
})
app.onSystemError((data) => {
  showBanner(t('system-backend-error', { msg: data.message }), 'error')
  appendLog(`Backend error: ${data.message}`, 'error')
})

// Auto-update
app.onUpdateAvailable((data) => {
  showUpdateBanner(t('update-available', { ver: data.version }), 'download')
})
app.onUpdateProgress((data) => {
  showUpdateBanner(t('update-downloading', { pct: data.pct }))
})
app.onUpdateReady(() => {
  showUpdateBanner(t('update-ready'), 'install')
})

// Helpers
function showResults (result) {
  document.getElementById('result-section').classList.remove('hidden')
  document.getElementById('stat-pages').textContent = result.pages_processed
  document.getElementById('stat-confidence').textContent = `${result.avg_confidence?.toFixed(1)}%`
  document.getElementById('stat-output').textContent = result.output_path

  const btn = document.getElementById('btn-open-output')
  btn.classList.remove('hidden')
  btn.onclick = () => {
    const { shell } = require('electron')
    shell.openPath(result.output_path)
  }
}

function showBanner (msg, type = 'warning') {
  const banner = document.getElementById('status-banner')
  banner.textContent = msg
  banner.className = type
  banner.classList.remove('hidden')
}

function showUpdateBanner (msg, action = null) {
  const banner  = document.getElementById('update-banner')
  const msgEl   = document.getElementById('update-message')
  const btnRestart = document.getElementById('btn-update-restart')
  const btnLater   = document.getElementById('btn-update-later')

  msgEl.textContent = msg
  banner.classList.remove('hidden')

  if (action === 'download') {
    btnLater.classList.remove('hidden')
    btnLater.onclick = () => {
      app.downloadUpdate()
      btnLater.classList.add('hidden')
    }
  } else if (action === 'install') {
    btnRestart.classList.remove('hidden')
    btnLater.classList.remove('hidden')
    btnRestart.onclick = () => app.installUpdate()
    btnLater.onclick   = () => banner.classList.add('hidden')
  }
}
