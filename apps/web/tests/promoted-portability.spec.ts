import fs from 'node:fs'

import { expect, test } from '@playwright/test'

type ProbeResult = {
  status?: string
  provider?: string
  inputName?: string
  inputShape?: number[]
  inputPattern?: string
  outputNames?: string[]
  outputs?: Record<
    string,
    {
      type?: string
      dims?: number[]
      sample?: number[]
      summary?: { min?: number; max?: number; mean?: number }
    }
  >
  elapsedMs?: number
}

type Reference = {
  model_sha256: string
  input_name: string
  output_name: string
  output_shape: number[]
  patterns: Record<
    string,
    {
      sample: number[]
      summary: { min: number; max: number; mean: number }
    }
  >
}

const modelUrl = process.env.B4_MODEL_URL
const referencePath = process.env.B4_REFERENCE_JSON
const evidencePath = process.env.B4_BROWSER_EVIDENCE_JSON

test.skip(!modelUrl || !referencePath || !evidencePath, 'B4 promoted model inputs are not configured')

test('promoted weld model matches Python ORT reference through ORT Web/WASM', async ({ page }) => {
  const reference = JSON.parse(
    fs.readFileSync(referencePath ?? '', 'utf8'),
  ) as Reference

  const patterns = ['zero', 'fill114', 'ramp251']
  const evidence: Array<Record<string, unknown>> = []

  for (const pattern of patterns) {
    await page.goto(
      `/portability.html?provider=wasm&model=${encodeURIComponent(
        modelUrl ?? '',
      )}&input=${pattern}`,
    )

    await page.getByRole('button', { name: 'Run probe' }).click()

    const output = page.locator('#output')
    await expect(output).toContainText('"status": "PASS"', { timeout: 60_000 })

    const raw = await output.textContent()
    expect(raw).not.toBeNull()
    const result = JSON.parse(raw ?? '{}') as ProbeResult
    const outputName = reference.output_name
    const actual = result.outputs?.[outputName]
    const expected = reference.patterns[pattern]

    expect(result.status).toBe('PASS')
    expect(result.provider).toBe('wasm')
    expect(result.inputName).toBe(reference.input_name)
    expect(result.inputShape).toEqual([1, 3, 416, 416])
    expect(result.inputPattern).toBe(pattern)
    expect(result.outputNames).toContain(outputName)
    expect(actual?.type).toBe('float32')
    expect(actual?.dims).toEqual(reference.output_shape)
    expect(actual?.sample?.length).toBe(expected.sample.length)

    const sampleDiffs = (actual?.sample ?? []).map((value, index) =>
      Math.abs(value - expected.sample[index]),
    )
    const maxSampleAbsDiff = Math.max(...sampleDiffs, 0)

    const actualSummary = actual?.summary
    const summaryDiffs = [
      Math.abs((actualSummary?.min ?? 0) - expected.summary.min),
      Math.abs((actualSummary?.max ?? 0) - expected.summary.max),
      Math.abs((actualSummary?.mean ?? 0) - expected.summary.mean),
    ]
    const maxSummaryAbsDiff = Math.max(...summaryDiffs)

    expect(maxSampleAbsDiff).toBeLessThanOrEqual(1e-3)
    expect(maxSummaryAbsDiff).toBeLessThanOrEqual(1e-3)

    evidence.push({
      pattern,
      provider: result.provider,
      inputName: result.inputName,
      inputShape: result.inputShape,
      outputName,
      output: actual,
      maxSampleAbsDiff,
      maxSummaryAbsDiff,
      elapsedMs: result.elapsedMs,
    })
  }

  fs.writeFileSync(
    evidencePath ?? '',
    JSON.stringify(
      {
        status: 'PASS',
        provider: 'wasm',
        modelSha256: reference.model_sha256,
        patterns: evidence,
      },
      null,
      2,
    ),
  )
})
