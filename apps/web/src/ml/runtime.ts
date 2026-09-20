import * as ort from 'onnxruntime-web'

export type RuntimeProvider = 'wasm'
export type RuntimePreference = 'auto' | 'wasm'

export interface RuntimeSession {
  session: ort.InferenceSession
  provider: RuntimeProvider
  warnings: string[]
}

export type RuntimeModelSource = string | Uint8Array

export async function createRuntimeSession(
  modelUrl: RuntimeModelSource,
  _preference: RuntimePreference = 'auto',
): Promise<RuntimeSession> {
  const session = await ort.InferenceSession.create(modelUrl, {
    executionProviders: ['wasm'],
  })

  return {
    session,
    provider: 'wasm',
    warnings: [],
  }
}
