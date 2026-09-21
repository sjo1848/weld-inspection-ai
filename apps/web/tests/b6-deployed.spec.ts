import fs from 'node:fs'
import path from 'node:path'

import { expect, test } from '@playwright/test'

const referenceImage = process.env.B6_REFERENCE_IMAGE
const evidencePath = process.env.B6_EVIDENCE_JSON
const screenshotPath = process.env.B6_SCREENSHOT

test.skip(
  !referenceImage || !evidencePath,
  'B6 deployed smoke inputs are not configured',
)

test('B6 deployed origin completes WASM analysis without uploading the image', async ({ page }) => {
  const requests: Array<{
    method: string
    url: string
    postDataBytes: number
  }> = []

  page.on('request', (request) => {
    const postData = request.postDataBuffer()
    requests.push({
      method: request.method(),
      url: request.url(),
      postDataBytes: postData?.byteLength ?? 0,
    })
  })

  await page.goto('/')

  await page.getByTestId('image-input').setInputFiles(referenceImage ?? '')
  await page.getByRole('button', { name: 'Analizar fotografía' }).click()

  const resultCard = page.getByTestId('result-card')
  const runtimeError = page.getByTestId('runtime-error')

  await Promise.race([
    resultCard.waitFor({ state: 'visible', timeout: 120_000 }),
    runtimeError.waitFor({ state: 'visible', timeout: 120_000 }),
  ])

  await expect(runtimeError).toHaveCount(0)
  await expect(resultCard).toBeVisible()

  const runtimeInfo = (await page.getByTestId('runtime-info').textContent()) ?? ''
  expect(runtimeInfo.toUpperCase()).toContain('WASM')

  const detectionCount = await page.getByTestId('detection-item').count()
  const zeroResult = (await page.getByTestId('zero-result').count()) > 0
  const summary = (await resultCard.textContent()) ?? ''

  const nonReadRequests = requests.filter(
    (request) => !['GET', 'HEAD'].includes(request.method),
  )
  const requestsWithBodies = requests.filter(
    (request) => request.postDataBytes > 0,
  )

  expect(nonReadRequests).toEqual([])
  expect(requestsWithBodies).toEqual([])

  if (screenshotPath) {
    await page.screenshot({
      path: screenshotPath,
      fullPage: true,
    })
  }

  const evidence = {
    stage: 'B6_DEPLOYED_SMOKE_COMPLETE',
    status: 'PASS',
    deployUrl: process.env.B6_DEPLOY_URL,
    referenceImage: path.basename(referenceImage ?? ''),
    runtimeInfo,
    detectionCount,
    zeroResult,
    resultSummary: summary.replace(/\s+/g, ' ').trim(),
    privacy: {
      requestCount: requests.length,
      nonReadRequestCount: nonReadRequests.length,
      requestBodiesCount: requestsWithBodies.length,
      requests,
      conclusion:
        'The selected validation image remained local; no POST/PUT/PATCH request or request body was observed during deployed inference.',
    },
    frozenTestUsed: false,
  }

  fs.writeFileSync(
    evidencePath ?? '',
    JSON.stringify(evidence, null, 2),
  )
})
