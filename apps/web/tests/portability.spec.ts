import { expect, test } from '@playwright/test'

test('official YOLOX-Nano reference graph executes through ORT Web/WASM', async ({ page }) => {
  await page.goto(
    '/portability.html?provider=wasm&model=/models/yolox_nano-coco-ref.onnx',
  )

  await page.getByRole('button', { name: 'Run probe' }).click()

  const output = page.locator('#output')
  await expect(output).toContainText('"status": "PASS"', { timeout: 60_000 })

  const raw = await output.textContent()
  expect(raw).not.toBeNull()
  const result = JSON.parse(raw ?? '{}') as {
    status?: string
    provider?: string
    inputShape?: number[]
    outputNames?: string[]
    outputs?: Record<string, { type?: string; dims?: number[] }>
    elapsedMs?: number
  }

  expect(result.status).toBe('PASS')
  expect(result.provider).toBe('wasm')
  expect(result.inputShape).toEqual([1, 3, 416, 416])
  expect(result.outputNames?.length ?? 0).toBeGreaterThan(0)
  expect(Object.keys(result.outputs ?? {}).length).toBeGreaterThan(0)
  expect(result.elapsedMs).toEqual(expect.any(Number))

  console.log(`B2_PORTABILITY_RESULT=${JSON.stringify(result)}`)
})
