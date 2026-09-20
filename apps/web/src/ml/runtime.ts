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
  const options: ort.InferenceSession.SessionOptions = {
    executionProviders: ['wasm'],
  }

  const session =
    typeof modelUrl === 'string'
      ? await ort.InferenceSession.create(modelUrl, options)
      : await ort.InferenceSession.create(modelUrl, options)

  return {
    session,
    provider: 'wasm',
    warnings: [],
  }
}
