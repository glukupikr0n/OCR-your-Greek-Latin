'use strict'

export class ProgressPanel {
  constructor () {
    this._container = document.getElementById('progress-container')
    this._bar = document.getElementById('progress-bar')
    this._text = document.getElementById('progress-text')
    this._conf = document.getElementById('progress-confidence')
  }

  start (totalPages) {
    this._container.classList.remove('hidden')
    this._bar.style.width = '0%'
    this._text.textContent = `Processing… (0 / ${totalPages} pages)`
    this._conf.textContent = ''
  }

  update (data) {
    const pct = Math.min(100, Math.max(0, data.pct || 0))
    this._bar.style.width = `${pct}%`
    this._text.textContent =
      `Processing page ${data.page + 1} of ${data.total_pages}… (${pct}%)`
    if (data.current_word_confidence != null) {
      this._conf.textContent =
        `Word confidence: ${data.current_word_confidence.toFixed(1)}%`
    }
  }

  finish (result) {
    this._bar.style.width = '100%'
    this._bar.style.background = 'var(--success)'
    this._text.textContent = `Done! ${result.pages_processed} pages processed.`
    this._conf.textContent =
      `Average confidence: ${result.avg_confidence?.toFixed(1)}%`
  }

  showError (message) {
    this._bar.style.background = 'var(--danger)'
    this._text.textContent = `Error: ${message}`
    this._conf.textContent = ''
  }

  showCancelled () {
    this._bar.style.background = 'var(--warning)'
    this._text.textContent = 'Processing cancelled.'
    this._conf.textContent = ''
  }
}
