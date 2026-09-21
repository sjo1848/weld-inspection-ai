import { defineConfig } from '@playwright/test'

const baseURL = process.env.B6_DEPLOY_URL

if (!baseURL) {
  throw new Error('B6_DEPLOY_URL is required for deployed smoke testing.')
}

export default defineConfig({
  testDir: './tests',
  timeout: 150_000,
  fullyParallel: false,
  workers: 1,
  reporter: 'line',
  use: {
    baseURL,
    browserName: 'chromium',
    headless: true,
    viewport: { width: 430, height: 932 },
  },
})
