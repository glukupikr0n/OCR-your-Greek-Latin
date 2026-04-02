'use strict'

import { t } from '../i18n.js'

export class FilePanel {
  constructor (app) {
    this._app = app
    this._currentFile = null
    this._totalPages = 0
    this.onFileLoaded = null

    this._bindEvents()
    this._bindGlobalDrop()
  }

  getCurrentFile () { return this._currentFile }
  getTotalPages () { return this._totalPages }

  async onSelectFile () {
    const path = await this._app.openFileDialog()
    if (path) await this._loadFile(path)
  }

  _bindEvents () {
    document.getElementById('btn-open-file').addEventListener('click', () => {
      this.onSelectFile()
    })

    document.getElementById('btn-change-file')?.addEventListener('click', () => {
      this._resetFileUI()
    })

    const dropZone = document.getElementById('drop-zone')

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault()
      e.stopPropagation()
      dropZone.classList.add('drag-over')
    })

    dropZone.addEventListener('dragleave', (e) => {
      if (!dropZone.contains(e.relatedTarget)) {
        dropZone.classList.remove('drag-over')
      }
    })

    dropZone.addEventListener('drop', async (e) => {
      e.preventDefault()
      e.stopPropagation()
      dropZone.classList.remove('drag-over')
      await this._handleDropEvent(e)
    })
  }

  // Allow dropping anywhere on the window
  _bindGlobalDrop () {
    document.addEventListener('dragover', (e) => {
      e.preventDefault()
      e.stopPropagation()
      if (!this._currentFile) {
        document.getElementById('drop-zone')?.classList.add('drag-over')
      }
    })

    document.addEventListener('dragleave', (e) => {
      // Only remove highlight when leaving the window entirely
      if (e.relatedTarget === null) {
        document.getElementById('drop-zone')?.classList.remove('drag-over')
      }
    })

    document.addEventListener('drop', async (e) => {
      e.preventDefault()
      e.stopPropagation()
      document.getElementById('drop-zone')?.classList.remove('drag-over')
      await this._handleDropEvent(e)
    })
  }

  async _handleDropEvent (e) {
    const files = e.dataTransfer?.files
    if (!files || files.length === 0) return

    const file = files[0]
    const filePath = file.path  // Electron provides .path on File objects

    if (!filePath) return

    const ext = filePath.split('.').pop().toLowerCase()
    const allowed = ['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp']
    if (!allowed.includes(ext)) {
      const meta = document.getElementById('file-meta-display')
      if (meta) {
        meta.textContent = `⚠ 지원하지 않는 형식: .${ext}`
        setTimeout(() => { if (meta.textContent.startsWith('⚠')) meta.textContent = '' }, 3000)
      } else {
        const hint = document.querySelector('.drop-hint')
        if (hint) {
          const orig = hint.textContent
          hint.textContent = `⚠ 지원하지 않는 형식: .${ext}`
          setTimeout(() => { hint.textContent = orig }, 3000)
        }
      }
      return
    }

    await this._loadFile(filePath)
  }

  async _loadFile (filePath) {
    this._currentFile = filePath
    const name = filePath.split('/').pop()

    document.getElementById('file-info').classList.remove('hidden')
    document.getElementById('drop-zone').classList.add('hidden')
    document.getElementById('file-name-display').textContent = name
    document.getElementById('file-meta-display').textContent = '…'

    try {
      const preview = await this._app.previewPage({ path: filePath, page: 0 })
      this._totalPages = preview.total_pages
      document.getElementById('file-meta-display').textContent =
        `${preview.total_pages} ${t('pages-unit')}`

      if (this.onFileLoaded) {
        this.onFileLoaded(filePath, preview.total_pages)
      }
    } catch (err) {
      document.getElementById('file-meta-display').textContent = '⚠ 파일 로드 실패'
      console.error('Error loading file:', err)
    }
  }

  _resetFileUI () {
    this._currentFile = null
    this._totalPages = 0
    document.getElementById('file-info').classList.add('hidden')
    document.getElementById('drop-zone').classList.remove('hidden')
    document.getElementById('btn-process').disabled = true
  }
}
