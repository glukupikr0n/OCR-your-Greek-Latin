'use strict'

const { ipcMain, dialog } = require('electron')

class IPCBridge {
  constructor (pythonManager) {
    this._python = pythonManager
    this._win = null
  }

  attachWindow (win) {
    this._win = win
  }

  registerIpcHandlers () {
    ipcMain.handle('ocr:process', (e, args) =>
      this._python.call('ocr.process', args))

    ipcMain.handle('ocr:cancel', (e, args) =>
      this._python.call('ocr.cancel', args))

    ipcMain.handle('ocr:train', (e, args) =>
      this._python.call('ocr.train', args))

    ipcMain.handle('pdf:preview', (e, args) =>
      this._python.call('pdf.preview', args))

    ipcMain.handle('pdf:split', (e, args) =>
      this._python.call('pdf.split', args))

    ipcMain.handle('system:check', () =>
      this._python.call('system.check', {}))

    ipcMain.handle('dialog:openFile', () => this._showOpenDialog())

    ipcMain.handle('dialog:saveFile', (e, args) => this._showSaveDialog(args))
  }

  forwardNotification (win, notification) {
    if (!win || win.isDestroyed()) return

    const method = notification.method
    if (method === 'ocr.progress') {
      win.webContents.send('ocr:progress', notification.params)
    } else if (method === 'ocr.train.progress') {
      win.webContents.send('ocr:train:progress', notification.params)
    }
  }

  async _showOpenDialog () {
    const result = await dialog.showOpenDialog(this._win, {
      title: 'Select PDF or Image',
      filters: [
        { name: 'PDF Files', extensions: ['pdf'] },
        { name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp'] },
        { name: 'All Files', extensions: ['*'] }
      ],
      properties: ['openFile']
    })
    if (result.canceled) return null
    return result.filePaths[0]
  }

  async _showSaveDialog (args = {}) {
    const result = await dialog.showSaveDialog(this._win, {
      title: args.title || 'Save Output PDF',
      defaultPath: args.defaultPath || 'output.pdf',
      filters: [
        { name: 'PDF Files', extensions: ['pdf'] }
      ]
    })
    if (result.canceled) return null
    return result.filePath
  }
}

module.exports = { IPCBridge }
