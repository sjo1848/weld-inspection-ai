import * as ort from 'onnxruntime-web/webgpu'

import { loadModelManifest, type ModelManifest } from './manifest'
import { preprocessCanvasSource } from './preprocess'
import { createRuntimeSession, type RuntimeProvider } from './runtime'
import { decodeYoloxRaw, type WeldDetection } from './yolox'

const MAX_IMAGE_BYTES = 20 * 1024 * 1024

export interface AnalysisResult {
  detections: WeldDetection[]
  imageWidth: number
  imageHeight: number
  provider: RuntimeProvider
  runtimeWarnings: string[]
  modelId: string
  modelVersion: string
  confidenceThreshold: number
}

interface LoadedAnalyzer {
  manifest: ModelManifest
  runtime: Awaited<ReturnType<typeof createRuntimeSession>>
}

let analyzerPromise: Promise<LoadedAnalyzer> | null = null

export async function analyzeImageFile(file: File): Promise<AnalysisResult> {
  validateImageFile(file)
  const analyzer = await getAnalyzer()
  const loaded = await loadImage(file)

  try {
    const preprocessed = preprocessCanvasSource(
      loaded.source,
      loaded.width,
      loaded.height,
      analyzer.manifest.inputWidth,
      analyzer.manifest.inputHeight,
    )

    const input = new ort.Tensor(
      'float32',
      preprocessed.data,
      [
        1,
        3,
        analyzer.manifest.inputHeight,
        analyzer.manifest.inputWidth,
      ],
    )

    const results = await analyzer.runtime.session.run({
      [analyzer.manifest.inputTensorName]: input,
    })

    const outputName = analyzer.manifest.outputTensorNames[0]
    const output = outputName ? results[outputName] : undefined
    if (!output) {
      throw new Error('El runtime no devolvió el tensor de salida esperado.')
    }

    const dims = Array.from(output.dims)
    if (JSON.stringify(dims) !== JSON.stringify([1, 3549, 8])) {
      throw new Error(
        `Forma de salida inesperada: [${dims.join(',')}].`,
      )
    }

    if (!(output.data instanceof Float32Array)) {
      throw new Error('El tensor de salida no es float32.')
    }

    const detections = decodeYoloxRaw(
      output.data,
      preprocessed.transform,
      analyzer.manifest,
    )

    return {
      detections,
      imageWidth: loaded.width,
      imageHeight: loaded.height,
      provider: analyzer.runtime.provider,
      runtimeWarnings: analyzer.runtime.warnings,
      modelId: analyzer.manifest.modelId,
      modelVersion: analyzer.manifest.modelVersion,
      confidenceThreshold: analyzer.manifest.confidenceThreshold,
    }
  } finally {
    loaded.close?.()
  }
}

async function getAnalyzer(): Promise<LoadedAnalyzer> {
  analyzerPromise ??= createAnalyzer()
  return analyzerPromise
}

async function createAnalyzer(): Promise<LoadedAnalyzer> {
  const manifest = await loadModelManifest()
  const response = await fetch(manifest.artifactPath, { cache: 'force-cache' })
  if (!response.ok) {
    throw new Error(`No se pudo cargar el modelo (HTTP ${response.status}).`)
  }

  const bytes = new Uint8Array(await response.arrayBuffer())
  if (bytes.byteLength !== manifest.artifactBytes) {
    throw new Error('El tamaño del modelo no coincide con el manifest promovido.')
  }

  const digest = await sha256Hex(bytes)
  if (digest !== manifest.artifactSha256) {
    throw new Error('La identidad SHA-256 del modelo no coincide con el manifest.')
  }

  const runtime = await createRuntimeSession(bytes, 'auto')
  if (!runtime.session.inputNames.includes(manifest.inputTensorName)) {
    throw new Error('El modelo cargado no expone el input esperado.')
  }

  for (const outputName of manifest.outputTensorNames) {
    if (!runtime.session.outputNames.includes(outputName)) {
      throw new Error('El modelo cargado no expone el output esperado.')
    }
  }

  return { manifest, runtime }
}

function validateImageFile(file: File): void {
  if (!file.type.startsWith('image/')) {
    throw new Error('Seleccioná un archivo de imagen válido.')
  }
  if (file.size <= 0) {
    throw new Error('La imagen seleccionada está vacía.')
  }
  if (file.size > MAX_IMAGE_BYTES) {
    throw new Error('La imagen supera el límite de 20 MB.')
  }
}

async function loadImage(file: File): Promise<{
  source: CanvasImageSource
  width: number
  height: number
  close?: () => void
}> {
  if (typeof createImageBitmap === 'function') {
    const bitmap = await createImageBitmap(file)
    return {
      source: bitmap,
      width: bitmap.width,
      height: bitmap.height,
      close: () => bitmap.close(),
    }
  }

  const url = URL.createObjectURL(file)
  try {
    const image = await new Promise<HTMLImageElement>((resolve, reject) => {
      const element = new Image()
      element.onload = () => resolve(element)
      element.onerror = () => reject(new Error('No se pudo decodificar la imagen.'))
      element.src = url
    })

    return {
      source: image,
      width: image.naturalWidth,
      height: image.naturalHeight,
    }
  } finally {
    URL.revokeObjectURL(url)
  }
}

async function sha256Hex(bytes: Uint8Array): Promise<string> {
  if (!globalThis.crypto?.subtle) {
    throw new Error('Este navegador no permite verificar la identidad del modelo.')
  }

  const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes)
  return Array.from(new Uint8Array(digest))
    .map((value) => value.toString(16).padStart(2, '0'))
    .join('')
}
