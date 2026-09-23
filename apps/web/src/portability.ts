import * as ort from 'onnxruntime-web/wasm'

import { createRuntimeSession, type RuntimePreference } from './ml/runtime'

type ProbePattern = 'zero' | 'fill114' | 'ramp251'

const outputElement = document.querySelector<HTMLPreElement>('#output')
const runButton = document.querySelector<HTMLButtonElement>('#run')

if (!outputElement || !runButton) {
  throw new Error('Portability probe DOM is incomplete')
}

const output = outputElement

runButton.addEventListener('click', () => {
  void runProbe()
})

async function runProbe(): Promise<void> {
  const params = new URLSearchParams(window.location.search)
  const modelUrl = params.get('model') ?? '/models/yolox_nano-coco-ref.onnx'
  const preference = parseProvider(params.get('provider'))
  const inputPattern = parseInputPattern(params.get('input'))

  setOutput({
    status: 'loading',
    modelUrl,
    requestedProvider: preference,
    inputPattern,
  })

  try {
    const runtime = await createRuntimeSession(modelUrl, preference)
    const inputName = runtime.session.inputNames[0]
    if (!inputName) {
      throw new Error('ONNX model exposes no input tensor')
    }

    const inputShape = [1, 3, 416, 416]
    const inputData = createProbeInput(inputPattern)
    const input = new ort.Tensor('float32', inputData, inputShape)

    const startedAt = performance.now()
    const results = await runtime.session.run({ [inputName]: input })
    const elapsedMs = performance.now() - startedAt

    setOutput({
      status: 'PASS',
      modelUrl,
      requestedProvider: preference,
      provider: runtime.provider,
      warnings: runtime.warnings,
      inputName,
      inputShape,
      inputPattern,
      outputNames: runtime.session.outputNames,
      outputs: Object.fromEntries(
        Object.entries(results).map(([name, value]) => {
          const tensor = value as ort.Tensor
          const data = tensor.data as Float32Array
          return [
            name,
            {
              type: tensor.type,
              dims: tensor.dims,
              sample: Array.from(data.slice(0, 32)),
              summary: summarize(data),
            },
          ]
        }),
      ),
      elapsedMs: Math.round(elapsedMs * 100) / 100,
    })
  } catch (error) {
    setOutput({
      status: 'FAIL',
      modelUrl,
      requestedProvider: preference,
      inputPattern,
      error: error instanceof Error ? error.message : String(error),
    })
  }
}

function createProbeInput(pattern: ProbePattern): Float32Array {
  const data = new Float32Array(3 * 416 * 416)

  if (pattern === 'fill114') {
    data.fill(114)
  } else if (pattern === 'ramp251') {
    for (let index = 0; index < data.length; index += 1) {
      data[index] = index % 251
    }
  }

  return data
}

function summarize(data: Float32Array): {
  min: number
  max: number
  mean: number
} {
  if (data.length === 0) {
    return { min: 0, max: 0, mean: 0 }
  }

  let min = Number.POSITIVE_INFINITY
  let max = Number.NEGATIVE_INFINITY
  let sum = 0

  for (const value of data) {
    min = Math.min(min, value)
    max = Math.max(max, value)
    sum += value
  }

  return {
    min,
    max,
    mean: sum / data.length,
  }
}

function parseInputPattern(value: string | null): ProbePattern {
  if (value === 'fill114' || value === 'ramp251') {
    return value
  }
  return 'zero'
}

function parseProvider(value: string | null): RuntimePreference {
  if (value === 'wasm') {
    return value
  }
  return 'auto'
}

function setOutput(value: unknown): void {
  output.textContent = JSON.stringify(value, null, 2)
}
