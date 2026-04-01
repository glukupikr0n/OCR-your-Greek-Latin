'use strict'

const { IPCBridge } = require('../../src/main/ipc-bridge')

// Mock electron
jest.mock('electron', () => ({
  ipcMain: {
    handle: jest.fn()
  },
  dialog: {
    showOpenDialog: jest.fn(),
    showSaveDialog: jest.fn()
  }
}), { virtual: true })

const { ipcMain, dialog } = require('electron')

describe('IPCBridge', () => {
  let pythonManager
  let bridge
  let win

  beforeEach(() => {
    pythonManager = {
      call: jest.fn()
    }
    bridge = new IPCBridge(pythonManager)
    win = {
      isDestroyed: jest.fn().mockReturnValue(false),
      webContents: {
        send: jest.fn()
      }
    }
    bridge.attachWindow(win)
    ipcMain.handle.mockClear()
    pythonManager.call.mockClear()
  })

  test('registerIpcHandlers registers all expected methods', () => {
    bridge.registerIpcHandlers()
    const registeredMethods = ipcMain.handle.mock.calls.map(([name]) => name)
    expect(registeredMethods).toContain('ocr:process')
    expect(registeredMethods).toContain('ocr:cancel')
    expect(registeredMethods).toContain('ocr:train')
    expect(registeredMethods).toContain('pdf:preview')
    expect(registeredMethods).toContain('pdf:split')
    expect(registeredMethods).toContain('system:check')
    expect(registeredMethods).toContain('dialog:openFile')
    expect(registeredMethods).toContain('dialog:saveFile')
  })

  test('ocr:process forwards to python manager', async () => {
    bridge.registerIpcHandlers()
    const handler = ipcMain.handle.mock.calls.find(([name]) => name === 'ocr:process')[1]
    const args = { input_path: '/tmp/test.pdf', output_path: '/tmp/out.pdf' }
    pythonManager.call.mockResolvedValue({ status: 'done' })

    await handler({}, args)
    expect(pythonManager.call).toHaveBeenCalledWith('ocr.process', args)
  })

  test('rejects promise on RPC error', async () => {
    bridge.registerIpcHandlers()
    const handler = ipcMain.handle.mock.calls.find(([name]) => name === 'ocr:process')[1]
    pythonManager.call.mockRejectedValue(new Error('Tesseract not found'))

    await expect(handler({}, {})).rejects.toThrow('Tesseract not found')
  })

  test('forwards ocr.progress notifications to webContents', () => {
    const notification = {
      method: 'ocr.progress',
      params: { page: 1, total_pages: 10, pct: 10 }
    }
    bridge.forwardNotification(win, notification)
    expect(win.webContents.send).toHaveBeenCalledWith('ocr:progress', notification.params)
  })

  test('does not forward to destroyed window', () => {
    win.isDestroyed.mockReturnValue(true)
    const notification = { method: 'ocr.progress', params: {} }
    bridge.forwardNotification(win, notification)
    expect(win.webContents.send).not.toHaveBeenCalled()
  })
})
