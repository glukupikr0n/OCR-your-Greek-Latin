'use strict'

export class TOCPanel {
  constructor () {
    this._section = document.getElementById('toc-section')
    this._list = document.getElementById('toc-list')
  }

  render (entries) {
    if (!entries || entries.length === 0) {
      this._section.classList.add('hidden')
      return
    }

    this._list.innerHTML = ''
    for (const entry of entries) {
      const li = document.createElement('li')
      li.className = `level-${entry.level}`
      const num = entry.display_num ? `${entry.display_num}. ` : ''
      li.textContent = `${num}${entry.title} (p.${entry.page_num + 1})`
      li.title = entry.title
      this._list.appendChild(li)
    }

    this._section.classList.remove('hidden')
  }

  clear () {
    this._list.innerHTML = ''
    this._section.classList.add('hidden')
  }
}
