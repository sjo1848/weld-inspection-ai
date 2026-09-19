export interface ModelManifest {
  stage: string
  modelId: string
  modelVersion: string
  artifactPath: string
  artifactSha256: string
  artifactBytes: number
  inputWidth: number
  inputHeight: number
  inputTensorName: string
  inputDtype: 'float32'
  inputLayout: 'NCHW'
  outputTensorNames: string[]
  outputTensorShapes: Record<string, number[]>
  rawOutputDecodedInModel: boolean
  classMap: Record<string, string>
  supportedClasses: string[]
  diagnosticOnlyClasses: string[]
  confidenceThreshold: number
  nmsThreshold: number
  preprocessingVersion: string
  postprocessingVersion: string
  toolingCommit: string
  limitations: string[]
}

export const DEFAULT_MANIFEST_URL = '/models/model-manifest.v0.1.json'

export async function loadModelManifest(
  url = DEFAULT_MANIFEST_URL,
): Promise<ModelManifest> {
  const response = await fetch(url, { cache: 'no-store' })
  if (!response.ok) {
    throw new Error(`No se pudo cargar el manifiesto del modelo (HTTP ${response.status}).`)
  }

  const manifest = (await response.json()) as ModelManifest
  validateManifest(manifest)
  return manifest
}

export function validateManifest(manifest: ModelManifest): void {
  if (manifest.stage !== 'B4_PROMOTED_MODEL_V0_1') {
    throw new Error('El manifiesto no corresponde al modelo promovido v0.1.')
  }
  if (
    manifest.inputWidth !== 416 ||
    manifest.inputHeight !== 416 ||
    manifest.inputTensorName !== 'images' ||
    manifest.inputDtype !== 'float32' ||
    manifest.inputLayout !== 'NCHW'
  ) {
    throw new Error('El contrato de entrada del modelo no coincide con B4.')
  }

  const outputName = manifest.outputTensorNames[0]
  const outputShape = outputName ? manifest.outputTensorShapes[outputName] : undefined
  if (
    outputName !== 'output' ||
    JSON.stringify(outputShape) !== JSON.stringify([1, 3549, 8])
  ) {
    throw new Error('El contrato de salida del modelo no coincide con B4.')
  }

  if (manifest.rawOutputDecodedInModel) {
    throw new Error('B5 requiere salida YOLOX raw para decodificar en el adapter.')
  }

  if (
    manifest.confidenceThreshold !== 0.2 ||
    manifest.nmsThreshold !== 0.65
  ) {
    throw new Error('Los thresholds del manifiesto no coinciden con el freeze B4.')
  }

  const supported = [...manifest.supportedClasses].sort()
  if (supported.join('|') !== ['slag inclusion', 'spatter'].sort().join('|')) {
    throw new Error('El conjunto de clases soportadas no coincide con B4.')
  }
}
