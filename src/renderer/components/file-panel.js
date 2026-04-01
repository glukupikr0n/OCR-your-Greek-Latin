'use strict'

export class FilePanel {
  constructor (app) {
    this._app = app
    this._currentFile = null
    this._totalPages = 0
    this.onFileLoaded = null

    this._bindEvents()
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

    const dropZone = document.getElementById('drop-zone')

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault()
      dropZone.classList.add('drag-over')
    })

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('drag-over')
    })

    dropZone.addEventListener('drop', async (e) => {
      e.preventDefault()
      dropZone.classList.remove('drag-over')
      const files = e.dataTransfer.files
      if (files.length > 0) {
        const path = files[0].path
        await this._loadFile(path)
      }
    })
  }

  async _loadFile (filePath) {
    this._currentFile = filePath
    const name = filePath.split('/').pop()

    // Show file info
    document.getElementById('file-info').classList.remove('hidden')
    document.getElementById('drop-zone').classList.add('hidden')
    document.getElementById('file-name-display').textContent = name

    // Get page count via preview request
    try {
      const preview = await this._app.previewPage({ path: filePath, page: 0 })
      this._totalPages = preview.total_pages
      document.getElementById('file-meta-display').textContent =
        `${preview.total_pages} page${preview.total_pages !== 1 ? 's' : ''}`

      if (this.onFileLoaded) {
        this.onFileLoaded(filePath, preview.total_pages)
      }
    } catch (err) {
      document.getElementById('file-meta-display').textContent = 'Error loading file'
      console.error('Error loading file:', err)
    }
  }
}
