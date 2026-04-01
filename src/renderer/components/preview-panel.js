'use strict'

export class PreviewPanel {
  constructor () {
    this._app = window.ocrApp
    this._canvas = document.getElementById('preview-canvas')
    this._placeholder = document.getElementById('preview-placeholder')
    this._pageNav = document.getElementById('page-nav')
    this._pageIndicator = document.getElementById('page-indicator')
    this._filePath = null
    this._currentPage = 0
    this.totalPages = 0

    document.getElementById('btn-prev-page').addEventListener('click', () => {
      if (this._currentPage > 0) this.showPage(this._currentPage - 1)
    })

    document.getElementById('btn-next-page').addEventListener('click', () => {
      if (this._currentPage < this.totalPages - 1) this.showPage(this._currentPage + 1)
    })
  }

  setFile (filePath, totalPages) {
    this._filePath = filePath
    this.totalPages = totalPages
    this._currentPage = 0
    if (totalPages > 1) {
      this._pageNav.classList.remove('hidden')
    }
  }

  async showPage (pageNum) {
    if (!this._filePath) return
    this._currentPage = pageNum
    this._pageIndicator.textContent = `Page ${pageNum + 1} / ${this.totalPages}`

    try {
      const result = await this._app.previewPage({
        path: this._filePath,
        page: pageNum,
        dpi: 100
      })
      this._renderBase64(result.image)
    } catch (err) {
      console.error('Preview error:', err)
    }
  }

  _renderBase64 (base64Png) {
    const img = new Image()
    img.onload = () => {
      this._canvas.width = img.width
      this._canvas.height = img.height
      const ctx = this._canvas.getContext('2d')
      ctx.drawImage(img, 0, 0)
      this._canvas.classList.remove('hidden')
      this._placeholder.classList.add('hidden')
    }
    img.src = `data:image/png;base64,${base64Png}`
  }
}
