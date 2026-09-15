import * as ort from 'onnxruntime-web/webgpu'

import { createRuntimeSession, type RuntimePreference } from './ml/runtime'

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

  setOutput({ status: 'loading', modelUrl, requestedProvider: preference })

  try {
    const runtime = await createRuntimeSession(modelUrl, preference)
    const inputName = runtime.session.inputNames[0]
    if (!inputName) {
      throw new Error('ONNX model exposes no input tensor')
    }

    // The official YOLOX-Nano reference export uses a fixed 1x3x416x416 input.
    // Any task-specific promoted export must be probed again rather than assuming parity.
    const inputShape = [1, 3, 416, 416]
    const input = new ort.Tensor('float32', new Float32Array(3 * 416 * 416), inputShape)

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
      outputNames: runtime.session.outputNames,
      outputs: Object.fromEntries(
        Object.entries(results).map(([name, value]) => {
          const tensor = value as ort.Tensor
          return [name, { type: tensor.type, dims: tensor.dims }]
        }),
      ),
      elapsedMs: Math.round(elapsedMs * 100) / 100,
    })
  } catch (error) {
    setOutput({
      status: 'FAIL',
      modelUrl,
      requestedProvider: preference,
      error: error instanceof Error ? error.message : String(error),
    })
  }
}

function parseProvider(value: string | null): RuntimePreference {
  if (value === 'wasm' || value === 'webgpu') {
    return value
  }
  return 'auto'
}

function setOutput(value: unknown): void {
  output.textContent = JSON.stringify(value, null, 2)
}
