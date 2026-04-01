'use strict'

export class OptionsPanel {
  getOptions () {
    const languages = []
    if (document.getElementById('lang-grc').checked) languages.push('grc')
    if (document.getElementById('lang-lat').checked) languages.push('lat')
    if (document.getElementById('lang-eng').checked) languages.push('eng')

    return {
      languages: languages.length > 0 ? languages : ['grc'],
      enhancement: {
        deskew: document.getElementById('opt-deskew').checked,
        grayscale: document.getElementById('opt-grayscale').checked,
        bw: document.getElementById('opt-bw').checked,
        denoise: document.getElementById('opt-denoise').checked,
        auto_contrast: document.getElementById('opt-autocontrast').checked,
        upscale_factor: parseInt(document.getElementById('opt-upscale').value, 10)
      },
      confidenceRetry: document.getElementById('opt-confidence-retry').checked,
      confidenceThreshold: parseInt(document.getElementById('opt-confidence-threshold').value, 10),
      layoutDetection: document.getElementById('opt-layout').checked,
      tocDetection: document.getElementById('opt-toc').checked,
      pageNumbering: document.getElementById('opt-page-numbers').checked,
      splitBilingual: document.getElementById('opt-split-bilingual').checked,
      threads: parseInt(document.getElementById('opt-threads').value, 10)
    }
  }
}
