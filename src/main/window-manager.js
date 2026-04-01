'use strict'

const { BrowserWindow } = require('electron')
const path = require('path')

class WindowManager {
  constructor () {
    this._mainWindow = null
  }

  createMainWindow () {
    this._mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 900,
      minHeight: 600,
      title: 'OCR Your Greek Latin',
      webPreferences: {
        preload: path.join(__dirname, '../preload/preload.js'),
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: false
      },
      show: false
    })

    this._mainWindow.loadFile(
      path.join(__dirname, '../renderer/index.html')
    )

    this._mainWindow.once('ready-to-show', () => {
      this._mainWindow.show()
    })

    this._mainWindow.on('closed', () => {
      this._mainWindow = null
    })

    if (process.env.NODE_ENV === 'development') {
      this._mainWindow.webContents.openDevTools()
    }

    return this._mainWindow
  }

  getMainWindow () {
    return this._mainWindow
  }
}

module.exports = { WindowManager }
