'use strict'

const { app, ipcMain, dialog } = require('electron')
const path = require('path')
const { WindowManager } = require('./window-manager')
const { PythonManager } = require('./python-manager')
const { IPCBridge } = require('./ipc-bridge')
const { buildMenu } = require('./menu')
const { setupAutoUpdater } = require('./auto-updater')

let windowManager
let pythonManager
let ipcBridge

app.whenReady().then(async () => {
  windowManager = new WindowManager()
  pythonManager = new PythonManager()
  ipcBridge = new IPCBridge(pythonManager)

  const win = windowManager.createMainWindow()

  pythonManager.onNotification = (notification) => {
    ipcBridge.forwardNotification(win, notification)
  }

  buildMenu(win, ipcBridge)

  try {
    await pythonManager.start()
  } catch (err) {
    console.error('Failed to start Python backend:', err)
    dialog.showErrorBox(
      'Backend Error',
      `Failed to start Python backend: ${err.message}\n\nPlease run scripts/install-mac.sh first.`
    )
    app.quit()
    return
  }

  ipcBridge.attachWindow(win)
  ipcBridge.registerIpcHandlers()

  // Verify dependencies on startup
  try {
    const sysInfo = await pythonManager.call('system.check', {})
    win.webContents.send('system:ready', sysInfo)
  } catch (err) {
    win.webContents.send('system:error', { message: err.message })
  }

  // Auto-updater
  setupAutoUpdater(win)
})

app.on('window-all-closed', () => {
  if (pythonManager) {
    pythonManager.stop()
  }
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (windowManager && windowManager.getMainWindow() === null) {
    const win = windowManager.createMainWindow()
    ipcBridge.attachWindow(win)
  }
})

app.on('before-quit', () => {
  if (pythonManager) {
    pythonManager.stop()
  }
})
