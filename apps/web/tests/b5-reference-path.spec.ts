import fs from 'node:fs'
import path from 'node:path'

import { expect, test } from '@playwright/test'

const referenceImage = process.env.B5_REFERENCE_IMAGE
const evidencePath = process.env.B5_EVIDENCE_JSON
const screenshotPath = process.env.B5_SCREENSHOT

test.skip(
  !referenceImage || !evidencePath,
  'B5 reference-path inputs are not configured',
)

test('B5 real image stays local and completes promoted-model analysis', async ({ page }) => {
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

  const input = page.getByTestId('image-input')
  await input.setInputFiles(referenceImage ?? '')

  await page.getByRole('button', { name: 'Analizar fotografía' }).click()

  const resultCard = page.getByTestId('result-card')
  const runtimeError = page.getByTestId('runtime-error')

  await Promise.race([
    resultCard.waitFor({ state: 'visible', timeout: 120_000 }),
    runtimeError.waitFor({ state: 'visible', timeout: 120_000 }),
  ])

  await expect(runtimeError).toHaveCount(0)
  await expect(resultCard).toBeVisible()

  const detectionCount = await page.getByTestId('detection-item').count()
  const zeroResult = (await page.getByTestId('zero-result').count()) > 0
  const runtimeInfo = (await page.getByTestId('runtime-info').textContent()) ?? ''
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
    status: 'PASS',
    referenceImage: path.basename(referenceImage ?? ''),
    detectionCount,
    zeroResult,
    runtimeInfo,
    resultSummary: summary.replace(/\s+/g, ' ').trim(),
    privacy: {
      requestCount: requests.length,
      nonReadRequestCount: nonReadRequests.length,
      requestBodiesCount: requestsWithBodies.length,
      requests,
      conclusion:
        'The selected image was provided through the local file input; no POST/PUT/PATCH request or request body was observed during the core analysis path.',
    },
  }

  fs.writeFileSync(
    evidencePath ?? '',
    JSON.stringify(evidence, null, 2),
  )
})
