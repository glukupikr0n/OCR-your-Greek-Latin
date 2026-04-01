'use strict'

// Import component modules
import { FilePanel } from './components/file-panel.js'
import { OptionsPanel } from './components/options-panel.js'
import { ProgressPanel } from './components/progress-panel.js'
import { PreviewPanel } from './components/preview-panel.js'
import { TOCPanel } from './components/toc-panel.js'

const app = window.ocrApp

// Instantiate panels
const filePanel = new FilePanel(app)
const optionsPanel = new OptionsPanel()
const progressPanel = new ProgressPanel()
const previewPanel = new PreviewPanel()
const tocPanel = new TOCPanel()

// Wiring: file loaded → enable process button
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
    title: 'Save Searchable PDF As…'
  })
  if (!outputPath) return

  const options = optionsPanel.getOptions()

  document.getElementById('btn-process').classList.add('hidden')
  document.getElementById('btn-cancel').classList.remove('hidden')
  progressPanel.start(previewPanel.totalPages)

  let currentJobId = null

  const progressHandler = (data) => {
    currentJobId = data.job_id
    progressPanel.update(data)
  }
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
        parallel_threads: options.threads
      }
    })

    progressPanel.finish(result)
    showResults(result)

    if (result.toc_entries && result.toc_entries.length > 0) {
      tocPanel.render(result.toc_entries)
    }
  } catch (err) {
    progressPanel.showError(err.message)
  } finally {
    app.offProgress(progressHandler)
    document.getElementById('btn-cancel').classList.add('hidden')
    document.getElementById('btn-process').classList.remove('hidden')
  }
})

// Cancel button
document.getElementById('btn-cancel').addEventListener('click', async () => {
  // The job_id is tracked internally; send a cancel without it — handler will find active job
  await app.cancelJob({})
  progressPanel.showCancelled()
  document.getElementById('btn-cancel').classList.add('hidden')
  document.getElementById('btn-process').classList.remove('hidden')
})

// Train button
document.getElementById('btn-train').addEventListener('click', () => {
  document.getElementById('train-dialog').classList.remove('hidden')
})

document.getElementById('btn-train-close').addEventListener('click', () => {
  document.getElementById('train-dialog').classList.add('hidden')
})

document.getElementById('btn-select-gt-dir').addEventListener('click', async () => {
  const path = await app.openFileDialog()
  if (path) {
    document.getElementById('train-gt-dir').value = path
  }
})

document.getElementById('btn-train-start').addEventListener('click', async () => {
  const gtDir = document.getElementById('train-gt-dir').value
  const baseLang = document.getElementById('train-base-lang').value
  const modelName = document.getElementById('train-model-name').value

  if (!gtDir) {
    alert('Please select a ground truth directory.')
    return
  }

  const trainProgressWrap = document.getElementById('train-progress-wrap')
  const trainProgressBar = document.getElementById('train-progress-bar')
  const trainProgressText = document.getElementById('train-progress-text')

  trainProgressWrap.classList.remove('hidden')

  const trainProgressHandler = (data) => {
    trainProgressBar.style.width = `${data.pct}%`
    trainProgressText.textContent = data.message
  }
  app.onTrainProgress(trainProgressHandler)

  try {
    const result = await app.trainModel({
      ground_truth_dir: gtDir,
      base_lang: baseLang,
      output_model_name: modelName
    })
    trainProgressText.textContent = `Done! Model saved to: ${result.output_path}`
  } catch (err) {
    trainProgressText.textContent = `Error: ${err.message}`
  } finally {
    app.offTrainProgress(trainProgressHandler)
  }
})

// Menu commands
app.onMenuCommand((cmd) => {
  if (cmd === 'menu:open-file') filePanel.onSelectFile()
  if (cmd === 'menu:process') document.getElementById('btn-process').click()
  if (cmd === 'menu:cancel') document.getElementById('btn-cancel').click()
  if (cmd === 'menu:train') document.getElementById('btn-train').click()
})

// System ready / error
app.onSystemReady((info) => {
  if (!info.ready) {
    const missing = info.languages?.missing?.join(', ') || ''
    const msg = missing
      ? `Missing Tesseract language data: ${missing}. Run scripts/install-mac.sh.`
      : 'System check: some dependencies may be missing.'
    showBanner(msg, 'warning')
  }
})

app.onSystemError((data) => {
  showBanner(`Backend error: ${data.message}`, 'error')
})

function showResults (result) {
  const section = document.getElementById('result-section')
  section.classList.remove('hidden')

  document.getElementById('stat-pages').textContent = result.pages_processed
  document.getElementById('stat-confidence').textContent =
    `${result.avg_confidence?.toFixed(1)}%`
  document.getElementById('stat-output').textContent = result.output_path

  const btnOpen = document.getElementById('btn-open-output')
  btnOpen.classList.remove('hidden')
  btnOpen.onclick = () => {
    // Open the file in the system's default PDF viewer
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
