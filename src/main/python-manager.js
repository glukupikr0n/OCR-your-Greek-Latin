'use strict'

const { spawn } = require('child_process')
const path = require('path')
const { v4: uuidv4 } = require('uuid')
const fs = require('fs')

class PythonManager {
  constructor () {
    this.process = null
    this.pendingRequests = new Map()
    this.onNotification = null
    this._buffer = ''
  }

  async start () {
    const { exe, args } = this._resolveBackend()

    this.process = spawn(exe, args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      env: {
        ...process.env,
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8'
      }
    })

    this.process.stdout.setEncoding('utf8')
    this.process.stderr.setEncoding('utf8')

    this.process.stdout.on('data', (chunk) => this._onStdout(chunk))
    this.process.stderr.on('data', (data) => {
      console.error('[Python stderr]', data.trim())
    })

    this.process.on('close', (code, signal) => {
      const reason = signal ? `signal ${signal}` : `code ${code}`
      console.log(`Python process exited with ${reason}`)
      // Reject all pending requests
      for (const [, { reject }] of this.pendingRequests) {
        reject(new Error(`Python process exited with ${reason}`))
      }
      this.pendingRequests.clear()
    })

    this.process.on('error', (err) => {
      console.error('Python process error:', err)
      for (const [, { reject }] of this.pendingRequests) {
        reject(err)
      }
      this.pendingRequests.clear()
    })

    // Wait briefly for the process to start
    await new Promise((resolve) => setTimeout(resolve, 200))

    if (this.process.exitCode !== null || this.process.signalCode !== null) {
      const reason = this.process.signalCode
        ? `signal ${this.process.signalCode}`
        : `exit code ${this.process.exitCode}`
      throw new Error(`Python process failed to start (${reason})`)
    }
  }

  stop () {
    if (this.process) {
      this.process.kill('SIGTERM')
      this.process = null
    }
  }

  call (method, params = {}) {
    return new Promise((resolve, reject) => {
      if (!this.process) {
        return reject(new Error('Python process is not running'))
      }

      const id = uuidv4()
      const request = {
        jsonrpc: '2.0',
        id,
        method,
        params
      }

      this.pendingRequests.set(id, { resolve, reject })

      const line = JSON.stringify(request) + '\n'
      this.process.stdin.write(line, 'utf8')
    })
  }

  _onStdout (chunk) {
    this._buffer += chunk
    const lines = this._buffer.split('\n')
    // Keep last incomplete line in buffer
    this._buffer = lines.pop()

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed) continue
      try {
        const msg = JSON.parse(trimmed)
        this._dispatch(msg)
      } catch (err) {
        console.error('[Python stdout parse error]', err.message, trimmed)
      }
    }
  }

  _dispatch (msg) {
    // Notification: id is null or missing
    if (msg.id === null || msg.id === undefined) {
      if (this.onNotification) {
        this.onNotification(msg)
      }
      return
    }

    const pending = this.pendingRequests.get(msg.id)
    if (!pending) {
      console.warn('[PythonManager] Received response for unknown id:', msg.id)
      return
    }

    this.pendingRequests.delete(msg.id)

    if (msg.error) {
      const err = new Error(msg.error.message || 'Unknown RPC error')
      err.code = msg.error.code
      err.data = msg.error.data
      pending.reject(err)
    } else {
      pending.resolve(msg.result)
    }
  }

  _resolveBackend () {
    const resourcesBase = process.resourcesPath || path.join(__dirname, '../../..')
    const devScriptPath = path.join(__dirname, '../../../python/main.py')

    // 1. PyInstaller standalone binary (production .app)
    const bundledBin = path.join(resourcesBase, 'scriptorium-backend')
    if (fs.existsSync(bundledBin)) {
      try { fs.chmodSync(bundledBin, '755') } catch (_) {}
      return { exe: bundledBin, args: [] }
    }

    // 2. Dev venv
    const devVenv = path.join(__dirname, '../../../python/.venv/bin/python3')
    if (fs.existsSync(devVenv)) {
      return { exe: devVenv, args: [devScriptPath] }
    }

    // 3. System python3 fallback
    return { exe: 'python3', args: [devScriptPath] }
  }
}

module.exports = { PythonManager }
