'use strict'

const { Menu, shell, app } = require('electron')

function buildMenu (win, ipcBridge) {
  const isMac = process.platform === 'darwin'

  const template = [
    ...(isMac ? [{
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    }] : []),
    {
      label: 'File',
      submenu: [
        {
          label: 'Open PDF...',
          accelerator: 'CmdOrCtrl+O',
          click: () => win.webContents.send('menu:open-file')
        },
        {
          label: 'Save Output As...',
          accelerator: 'CmdOrCtrl+Shift+S',
          click: () => win.webContents.send('menu:save-file')
        },
        { type: 'separator' },
        isMac ? { role: 'close' } : { role: 'quit' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' }
      ]
    },
    {
      label: 'OCR',
      submenu: [
        {
          label: 'Process File',
          accelerator: 'CmdOrCtrl+Return',
          click: () => win.webContents.send('menu:process')
        },
        {
          label: 'Cancel Processing',
          accelerator: 'Escape',
          click: () => win.webContents.send('menu:cancel')
        },
        { type: 'separator' },
        {
          label: 'Train Custom Model...',
          click: () => win.webContents.send('menu:train')
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About OCR Your Greek Latin',
          click: () => {
            const { dialog } = require('electron')
            dialog.showMessageBox(win, {
              type: 'info',
              title: 'About',
              message: 'OCR Your Greek Latin',
              detail: 'Desktop OCR for Ancient Greek and Latin manuscripts.\n\nPowered by Tesseract, pikepdf, and Electron.'
            })
          }
        }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

module.exports = { buildMenu }
