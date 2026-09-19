import * as ort from 'onnxruntime-web/webgpu'

export type RuntimeProvider = 'webgpu' | 'wasm'
export type RuntimePreference = 'auto' | RuntimeProvider

export interface RuntimeSession {
  session: ort.InferenceSession
  provider: RuntimeProvider
  warnings: string[]
}

export type RuntimeModelSource = string | Uint8Array

export async function createRuntimeSession(
  modelUrl: RuntimeModelSource,
  preference: RuntimePreference = 'auto',
): Promise<RuntimeSession> {
  const warnings: string[] = []

  if (preference === 'wasm') {
    const session = await createSession(modelUrl, 'wasm')
    return { session, provider: 'wasm', warnings }
  }

  if (preference === 'webgpu') {
    if (!hasWebGpu()) {
      throw new Error('WebGPU was explicitly requested but is not available in this browser.')
    }
    const session = await createSession(modelUrl, 'webgpu')
    return { session, provider: 'webgpu', warnings }
  }

  if (hasWebGpu()) {
    try {
      const session = await createSession(modelUrl, 'webgpu')
      return { session, provider: 'webgpu', warnings }
    } catch (error) {
      warnings.push(`WebGPU initialization failed: ${toErrorMessage(error)}`)
    }
  } else {
    warnings.push('WebGPU is not available in this browser; using WebAssembly.')
  }

  const session = await createSession(modelUrl, 'wasm')
  return { session, provider: 'wasm', warnings }
}

function createSession(
  modelUrl: RuntimeModelSource,
  provider: RuntimeProvider,
): Promise<ort.InferenceSession> {
  const options: ort.InferenceSession.SessionOptions = {
    executionProviders: [provider],
  }

  if (typeof modelUrl === 'string') {
    return ort.InferenceSession.create(modelUrl, options)
  }
  return ort.InferenceSession.create(modelUrl, options)
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
