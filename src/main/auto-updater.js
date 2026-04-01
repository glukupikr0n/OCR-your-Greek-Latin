'use strict'

const { ipcMain } = require('electron')

let _autoUpdater = null

function setupAutoUpdater (win) {
  // electron-updater is optional — skip gracefully in dev or if not installed
  try {
    const { autoUpdater } = require('electron-updater')
    _autoUpdater = autoUpdater

    autoUpdater.autoDownload = false
    autoUpdater.autoInstallOnAppQuit = true

    autoUpdater.on('update-available', (info) => {
      win.webContents.send('update:available', {
        version: info.version,
        releaseNotes: info.releaseNotes
      })
    })

    autoUpdater.on('update-not-available', () => {
      win.webContents.send('update:none')
    })

    autoUpdater.on('download-progress', (progress) => {
      win.webContents.send('update:progress', {
        pct: Math.round(progress.percent),
        speed: progress.bytesPerSecond,
        transferred: progress.transferred,
        total: progress.total
      })
    })

    autoUpdater.on('update-downloaded', () => {
      win.webContents.send('update:ready')
    })

    autoUpdater.on('error', (err) => {
      console.error('Auto-updater error:', err)
    })

    // Check for updates 5 seconds after launch
    setTimeout(() => {
      autoUpdater.checkForUpdates().catch((err) => {
        console.warn('Update check failed:', err.message)
      })
    }, 5000)
  } catch (err) {
    // electron-updater not available (dev mode without the package)
    console.warn('Auto-updater not available:', err.message)
  }

  // IPC handlers
  ipcMain.handle('update:check', () => {
    return _autoUpdater?.checkForUpdates().catch(() => null)
  })

  ipcMain.handle('update:download', () => {
    return _autoUpdater?.downloadUpdate().catch(() => null)
  })

  ipcMain.handle('update:install', () => {
    _autoUpdater?.quitAndInstall()
  })
}

module.exports = { setupAutoUpdater }
