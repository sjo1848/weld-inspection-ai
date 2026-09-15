import * as ort from 'onnxruntime-web/webgpu'

export type RuntimeProvider = 'webgpu' | 'wasm'

export interface RuntimeSession {
  session: ort.InferenceSession
  provider: RuntimeProvider
  warnings: string[]
}

export async function createRuntimeSession(modelUrl: string): Promise<RuntimeSession> {
  const warnings: string[] = []

  if (hasWebGpu()) {
    try {
      const session = await ort.InferenceSession.create(modelUrl, {
        executionProviders: ['webgpu'],
      })
      return { session, provider: 'webgpu', warnings }
    } catch (error) {
      warnings.push(`WebGPU initialization failed: ${toErrorMessage(error)}`)
    }
  } else {
    warnings.push('WebGPU is not available in this browser; using WebAssembly.')
  }

  const session = await ort.InferenceSession.create(modelUrl, {
    executionProviders: ['wasm'],
  })
  return { session, provider: 'wasm', warnings }
}

function hasWebGpu(): boolean {
  if (typeof navigator === 'undefined') {
    return false
  }
  return 'gpu' in navigator
}

function toErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}
