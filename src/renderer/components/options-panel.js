'use strict'

export class OptionsPanel {
  constructor () {
    this._bindSubSettings()
  }

  // Show/hide sub-settings when checkbox toggled
  _bindSubSettings () {
    const pairs = [
      ['opt-deskew',            'sub-deskew'],
      ['opt-denoise',           'sub-denoise'],
      ['opt-upscale-on',        'sub-upscale'],
      ['opt-confidence-retry',  'sub-confidence'],
      ['opt-split-bilingual',   'sub-split'],
    ]

    for (const [checkId, subId] of pairs) {
      const checkbox = document.getElementById(checkId)
      const sub = document.getElementById(subId)
      if (!checkbox || !sub) continue

      // Set initial state
      sub.classList.toggle('hidden', !checkbox.checked)

      checkbox.addEventListener('change', () => {
        sub.classList.toggle('hidden', !checkbox.checked)
      })
    }
  }

  getOptions () {
    const languages = []
    if (document.getElementById('lang-grc').checked) languages.push('grc')
    if (document.getElementById('lang-lat').checked) languages.push('lat')
    if (document.getElementById('lang-eng').checked) languages.push('eng')

    const upscaleOn = document.getElementById('opt-upscale-on').checked
    const upscaleFactor = upscaleOn
      ? parseInt(document.getElementById('opt-upscale').value, 10)
      : 1

    return {
      languages: languages.length > 0 ? languages : ['grc'],
      enhancement: {
        deskew: document.getElementById('opt-deskew').checked,
        grayscale: document.getElementById('opt-grayscale').checked,
        bw: document.getElementById('opt-bw').checked,
        denoise: document.getElementById('opt-denoise').checked,
        denoise_strength: parseInt(document.getElementById('opt-denoise-strength').value, 10),
        auto_contrast: document.getElementById('opt-autocontrast').checked,
        upscale_factor: upscaleFactor
      },
      confidenceRetry: document.getElementById('opt-confidence-retry').checked,
      confidenceThreshold: parseInt(document.getElementById('opt-confidence-threshold').value, 10),
      layoutDetection: document.getElementById('opt-layout').checked,
      tocDetection: document.getElementById('opt-toc').checked,
      pageNumbering: document.getElementById('opt-page-numbers').checked,
      splitBilingual: document.getElementById('opt-split-bilingual').checked,
      splitLangA: document.getElementById('opt-split-lang-a').value || 'greek',
      splitLangB: document.getElementById('opt-split-lang-b').value || 'latin',
      threads: parseInt(document.getElementById('opt-threads').value, 10)
    }
  }
}
