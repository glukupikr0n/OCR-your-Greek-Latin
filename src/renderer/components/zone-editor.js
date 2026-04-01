'use strict'

/**
 * ZoneEditor — Interactive zone overlay on top of the preview canvas.
 *
 * Zones are stored as normalized [0,1] coordinates.
 * The overlay div is absolutely-positioned over the canvas.
 */
export class ZoneEditor {
  constructor () {
    this._canvas = document.getElementById('preview-canvas')
    this._overlay = document.getElementById('zone-overlay')
    this._zones = []      // [{id, x0, y0, x1, y1, psm, lang, label}]
    this._active = false
    this._nextId = 1

    this._canvas.addEventListener('mousedown', (e) => this._onCanvasMousedown(e))
    new ResizeObserver(() => this._renderZones()).observe(this._canvas)
  }

  setActive (active) {
    this._active = active
    this._overlay.style.display = active ? 'block' : 'none'
    if (active) this._renderZones()
  }

  setZones (zones) {
    this._zones = zones.map((z, i) => ({ id: this._nextId++, ...z }))
    this._renderZones()
  }

  getZones () {
    return this._zones.map(({ id, ...rest }) => rest)
  }

  clearZones () {
    this._zones = []
    this._renderZones()
  }

  _renderZones () {
    if (!this._overlay) return
    this._overlay.innerHTML = ''

    const canvasRect = this._canvas.getBoundingClientRect()
    const overlayRect = this._overlay.parentElement.getBoundingClientRect()

    const offX = canvasRect.left - overlayRect.left
    const offY = canvasRect.top - overlayRect.top
    const cw = canvasRect.width
    const ch = canvasRect.height

    for (const zone of this._zones) {
      const box = this._makeZoneBox(zone, offX, offY, cw, ch)
      this._overlay.appendChild(box)
    }
  }

  _makeZoneBox (zone, offX, offY, cw, ch) {
    const div = document.createElement('div')
    div.className = 'zone-box'
    div.dataset.zoneId = zone.id

    const px = (zone.x0 * cw + offX)
    const py = (zone.y0 * ch + offY)
    const pw = (zone.x1 - zone.x0) * cw
    const ph = (zone.y1 - zone.y0) * ch

    div.style.left   = `${px}px`
    div.style.top    = `${py}px`
    div.style.width  = `${pw}px`
    div.style.height = `${ph}px`

    // Label
    if (zone.label) {
      const lbl = document.createElement('span')
      lbl.className = 'zone-label'
      lbl.textContent = zone.label
      div.appendChild(lbl)
    }

    // Delete button
    const del = document.createElement('button')
    del.className = 'zone-delete'
    del.textContent = '✕'
    del.addEventListener('click', (e) => {
      e.stopPropagation()
      this._zones = this._zones.filter(z => z.id !== zone.id)
      this._renderZones()
    })
    div.appendChild(del)

    // Drag to move
    div.addEventListener('mousedown', (e) => {
      if (e.target === del) return
      e.preventDefault()
      const startX = e.clientX
      const startY = e.clientY
      const origX0 = zone.x0, origY0 = zone.y0, origX1 = zone.x1, origY1 = zone.y1

      const onMove = (me) => {
        const dx = (me.clientX - startX) / cw
        const dy = (me.clientY - startY) / ch
        const w = origX1 - origX0
        const h = origY1 - origY0
        zone.x0 = Math.max(0, Math.min(1 - w, origX0 + dx))
        zone.y0 = Math.max(0, Math.min(1 - h, origY0 + dy))
        zone.x1 = zone.x0 + w
        zone.y1 = zone.y0 + h
        this._renderZones()
      }
      const onUp = () => {
        document.removeEventListener('mousemove', onMove)
        document.removeEventListener('mouseup', onUp)
      }
      document.addEventListener('mousemove', onMove)
      document.addEventListener('mouseup', onUp)
    })

    // Resize handle (bottom-right)
    const handle = document.createElement('div')
    handle.className = 'zone-resize'
    handle.addEventListener('mousedown', (e) => {
      e.preventDefault()
      e.stopPropagation()
      const startX = e.clientX
      const startY = e.clientY
      const origX1 = zone.x1, origY1 = zone.y1

      const onMove = (me) => {
        zone.x1 = Math.max(zone.x0 + 0.02, Math.min(1, origX1 + (me.clientX - startX) / cw))
        zone.y1 = Math.max(zone.y0 + 0.02, Math.min(1, origY1 + (me.clientY - startY) / ch))
        this._renderZones()
      }
      const onUp = () => {
        document.removeEventListener('mousemove', onMove)
        document.removeEventListener('mouseup', onUp)
      }
      document.addEventListener('mousemove', onMove)
      document.addEventListener('mouseup', onUp)
    })
    div.appendChild(handle)

    return div
  }

  // Draw new zone by dragging on empty canvas area
  _onCanvasMousedown (e) {
    if (!this._active) return
    if (e.target !== this._canvas) return
    e.preventDefault()

    const canvasRect = this._canvas.getBoundingClientRect()
    const overlayRect = this._overlay.parentElement.getBoundingClientRect()
    const cw = canvasRect.width
    const ch = canvasRect.height

    const startNX = (e.clientX - canvasRect.left) / cw
    const startNY = (e.clientY - canvasRect.top) / ch

    const newZone = {
      id: this._nextId++,
      x0: startNX, y0: startNY,
      x1: startNX, y1: startNY,
      psm: 3, lang: '', label: `Zone ${this._zones.length + 1}`
    }
    this._zones.push(newZone)

    const onMove = (me) => {
      const nx = (me.clientX - canvasRect.left) / cw
      const ny = (me.clientY - canvasRect.top) / ch
      newZone.x0 = Math.min(startNX, nx)
      newZone.y0 = Math.min(startNY, ny)
      newZone.x1 = Math.max(startNX, nx)
      newZone.y1 = Math.max(startNY, ny)
      this._renderZones()
    }
    const onUp = () => {
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
      // Remove tiny accidental zones
      if ((newZone.x1 - newZone.x0) < 0.02 || (newZone.y1 - newZone.y0) < 0.02) {
        this._zones = this._zones.filter(z => z.id !== newZone.id)
        this._renderZones()
      }
    }
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
  }
}
