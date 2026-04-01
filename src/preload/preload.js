'use strict'

const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('ocrApp', {
  // File dialogs
  openFileDialog: () => ipcRenderer.invoke('dialog:openFile'),
  saveFileDialog: (args) => ipcRenderer.invoke('dialog:saveFile', args),

  // OCR commands
  processFile: (args) => ipcRenderer.invoke('ocr:process', args),
  cancelJob: (args) => ipcRenderer.invoke('ocr:cancel', args),
  trainModel: (args) => ipcRenderer.invoke('ocr:train', args),

  // PDF commands
  previewPage: (args) => ipcRenderer.invoke('pdf:preview', args),
  splitBilingual: (args) => ipcRenderer.invoke('pdf:split', args),

  // System
  systemCheck: () => ipcRenderer.invoke('system:check'),

  // Events: OCR progress
  onProgress: (cb) => {
    ipcRenderer.on('ocr:progress', (_, data) => cb(data))
  },
  offProgress: (cb) => {
    ipcRenderer.removeListener('ocr:progress', cb)
  },

  // Events: training progress
  onTrainProgress: (cb) => {
    ipcRenderer.on('ocr:train:progress', (_, data) => cb(data))
  },
  offTrainProgress: (cb) => {
    ipcRenderer.removeListener('ocr:train:progress', cb)
  },

  // Events: system ready / error
  onSystemReady: (cb) => {
    ipcRenderer.on('system:ready', (_, data) => cb(data))
  },
  onSystemError: (cb) => {
    ipcRenderer.on('system:error', (_, data) => cb(data))
  },

  // Events: menu commands
  onMenuCommand: (cb) => {
    const events = ['menu:open-file', 'menu:save-file', 'menu:process', 'menu:cancel', 'menu:train']
    events.forEach((evt) => {
      ipcRenderer.on(evt, () => cb(evt))
    })
  },

  // Auto-update
  checkForUpdate: () => ipcRenderer.invoke('update:check'),
  downloadUpdate: () => ipcRenderer.invoke('update:download'),
  installUpdate: () => ipcRenderer.invoke('update:install'),
  onUpdateAvailable: (cb) => ipcRenderer.on('update:available', (_, data) => cb(data)),
  onUpdateProgress: (cb) => ipcRenderer.on('update:progress', (_, data) => cb(data)),
  onUpdateReady:    (cb) => ipcRenderer.on('update:ready',    ()       => cb()),
  onUpdateNone:     (cb) => ipcRenderer.on('update:none',     ()       => cb()),
})
