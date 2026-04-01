'use strict'

const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('ocrApp', {
  // File dialogs
  openFileDialog: () => ipcRenderer.invoke('dialog:openFile'),
  saveFileDialog: (args) => ipcRenderer.invoke('dialog:saveFile', args),

  // OCR commands
  processFile: (args) => ipcRenderer.invoke('ocr:process', args),
  cancelJob: (args) => ipcRenderer.invoke('ocr:cancel', args),

  // PDF commands
  previewPage: (args) => ipcRenderer.invoke('pdf:preview', args),
  splitBilingual: (args) => ipcRenderer.invoke('pdf:split', args),

  // System
  systemCheck: () => ipcRenderer.invoke('system:check'),

  // Data download
  dataListSources: () => ipcRenderer.invoke('data:listSources'),
  dataDownloadTessdata: (args) => ipcRenderer.invoke('data:downloadTessdata', args),
  dataDownloadCorpus: (args) => ipcRenderer.invoke('data:downloadCorpus', args),
  onDataProgress: (cb) => ipcRenderer.on('data:progress', (_, data) => cb(data)),
  offDataProgress: (cb) => ipcRenderer.removeListener('data:progress', cb),

  // File dialogs
  openDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),

  // Events: OCR progress
  onProgress: (cb) => {
    ipcRenderer.on('ocr:progress', (_, data) => cb(data))
  },
  offProgress: (cb) => {
    ipcRenderer.removeListener('ocr:progress', cb)
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
    const events = ['menu:open-file', 'menu:save-file', 'menu:process', 'menu:cancel']
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
