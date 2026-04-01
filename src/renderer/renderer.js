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

  document.getElementById('btn-process').classList.add('hidden')
  document.getElementById('btn-cancel').classList.remove('hidden')
  progressPanel.start(previewPanel.totalPages)

  const progressHandler = (data) => progressPanel.update(data)
  app.onProgress(progressHandler)

  try {
    const result = await app.processFile({
      input_path: filePath,
      output_path: outputPath,
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
        parallel_threads: options.threads
      }
    })

    progressPanel.finish(result)
    showResults(result)
    if (result.toc_entries?.length > 0) tocPanel.render(result.toc_entries)

  } catch (err) {
    progressPanel.showError(err.message)
  } finally {
    app.offProgress(progressHandler)
    document.getElementById('btn-cancel').classList.add('hidden')
    document.getElementById('btn-process').classList.remove('hidden')
  }
})

// Cancel
document.getElementById('btn-cancel').addEventListener('click', async () => {
  await app.cancelJob({})
  progressPanel.showCancelled()
  document.getElementById('btn-cancel').classList.add('hidden')
  document.getElementById('btn-process').classList.remove('hidden')
})

// Train dialog
document.getElementById('btn-train').addEventListener('click', () => {
  document.getElementById('train-dialog').classList.remove('hidden')
})
document.getElementById('btn-train-close').addEventListener('click', () => {
  document.getElementById('train-dialog').classList.add('hidden')
})
document.getElementById('btn-select-gt-dir').addEventListener('click', async () => {
  const path = await app.openFileDialog()
  if (path) document.getElementById('train-gt-dir').value = path
})
document.getElementById('btn-train-start').addEventListener('click', async () => {
  const gtDir = document.getElementById('train-gt-dir').value
  if (!gtDir) { alert('Ground truth 디렉토리를 선택하세요.'); return }

  const wrap = document.getElementById('train-progress-wrap')
  const bar  = document.getElementById('train-progress-bar')
  const txt  = document.getElementById('train-progress-text')
  wrap.classList.remove('hidden')

  const handler = (data) => {
    bar.style.width = `${data.pct}%`
    txt.textContent = data.message
  }
  app.onTrainProgress(handler)

  try {
    const result = await app.trainModel({
      ground_truth_dir: gtDir,
      base_lang: document.getElementById('train-base-lang').value,
      output_model_name: document.getElementById('train-model-name').value
    })
    txt.textContent = `완료: ${result.output_path}`
  } catch (err) {
    txt.textContent = `오류: ${err.message}`
  } finally {
    app.offTrainProgress(handler)
  }
})

// Menu commands
app.onMenuCommand((cmd) => {
  if (cmd === 'menu:open-file') filePanel.onSelectFile()
  if (cmd === 'menu:process')   document.getElementById('btn-process').click()
  if (cmd === 'menu:cancel')    document.getElementById('btn-cancel').click()
  if (cmd === 'menu:train')     document.getElementById('btn-train').click()
})

// System ready / error
app.onSystemReady((info) => {
  if (!info.ready) {
    const missing = info.languages?.missing?.join(', ') || ''
    showBanner(t('system-missing-langs', { langs: missing }), 'warning')
  }
})
app.onSystemError((data) => {
  showBanner(t('system-backend-error', { msg: data.message }), 'error')
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
