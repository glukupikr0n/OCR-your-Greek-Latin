/**
 * End-to-end tests using Playwright.
 * Requires the app to be built or running in development mode.
 *
 * Run with: npx playwright test tests/e2e
 */

const { test, expect } = require('@playwright/test')
const { _electron: electron } = require('playwright')
const path = require('path')

let app
let page

test.beforeAll(async () => {
  app = await electron.launch({
    args: [path.join(__dirname, '../../')],
    env: {
      ...process.env,
      NODE_ENV: 'test'
    }
  })
  page = await app.firstWindow()
  await page.waitForLoadState('domcontentloaded')
})

test.afterAll(async () => {
  if (app) await app.close()
})

test('app window opens and shows file drop zone', async () => {
  const dropZone = page.locator('#drop-zone')
  await expect(dropZone).toBeVisible()
})

test('open file button is present and enabled', async () => {
  const btn = page.locator('#btn-open-file')
  await expect(btn).toBeVisible()
  await expect(btn).toBeEnabled()
})

test('process button is initially disabled', async () => {
  const btn = page.locator('#btn-process')
  await expect(btn).toBeDisabled()
})

test('train button opens training dialog', async () => {
  const btnTrain = page.locator('#btn-train')
  await btnTrain.click()
  const dialog = page.locator('#train-dialog')
  await expect(dialog).toBeVisible()
  await page.locator('#btn-train-close').click()
  await expect(dialog).toBeHidden()
})

test('preview canvas is hidden initially', async () => {
  const canvas = page.locator('#preview-canvas')
  await expect(canvas).toBeHidden()
})

test('right panel result section is hidden initially', async () => {
  const section = page.locator('#result-section')
  await expect(section).toBeHidden()
})
