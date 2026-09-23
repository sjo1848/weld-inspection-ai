import type { ModelManifest } from './manifest'
import type { ImageTransform } from './preprocess'

export interface DetectionBox {
  x: number
  y: number
  width: number
  height: number
}

export interface WeldDetection {
  classId: number
  label: string
  confidence: number
  box: DetectionBox
}

interface ModelDetection extends WeldDetection {
  modelBox: DetectionBox
}

const STRIDES = [8, 16, 32] as const

export function decodeYoloxRaw(
  data: Float32Array,
  transform: ImageTransform,
  manifest: ModelManifest,
): WeldDetection[] {
  const attributes = 5 + Object.keys(manifest.classMap).length
  const expected = 3549 * attributes
  if (data.length !== expected) {
    throw new Error(
      `Salida YOLOX inesperada: ${data.length} valores; se esperaban ${expected}.`,
    )
  }

  const supported = new Set(manifest.supportedClasses)
  const candidates: ModelDetection[] = []
  let anchor = 0

  for (const stride of STRIDES) {
    const gridWidth = Math.floor(manifest.inputWidth / stride)
    const gridHeight = Math.floor(manifest.inputHeight / stride)

    for (let gy = 0; gy < gridHeight; gy += 1) {
      for (let gx = 0; gx < gridWidth; gx += 1) {
        const base = anchor * attributes
        const tx = data[base] ?? 0
        const ty = data[base + 1] ?? 0
        const tw = data[base + 2] ?? 0
        const th = data[base + 3] ?? 0
        const objectness = data[base + 4] ?? 0

        let bestClass = 0
        let bestClassProbability = -Infinity
        for (let classId = 0; classId < attributes - 5; classId += 1) {
          const probability = data[base + 5 + classId] ?? 0
          if (probability > bestClassProbability) {
            bestClassProbability = probability
            bestClass = classId
          }
        }

        const confidence = objectness * bestClassProbability
        const label = manifest.classMap[String(bestClass)]

        if (
          confidence >= manifest.confidenceThreshold &&
          label &&
          supported.has(label)
        ) {
          const centerX = (tx + gx) * stride
          const centerY = (ty + gy) * stride
          const width = Math.exp(tw) * stride
          const height = Math.exp(th) * stride
          const modelBox = {
            x: centerX - width / 2,
            y: centerY - height / 2,
            width,
            height,
          }

          candidates.push({
            classId: bestClass,
            label,
            confidence,
            box: modelBox,
            modelBox,
          })
        }

        anchor += 1
      }
    }
  }

  return classAwareNms(candidates, manifest.nmsThreshold)
    .map((detection) => ({
      classId: detection.classId,
      label: detection.label,
      confidence: detection.confidence,
      box: reverseLetterbox(detection.modelBox, transform),
    }))
    .sort((a, b) => b.confidence - a.confidence)
}

export function classAwareNms<T extends WeldDetection>(
  detections: T[],
  iouThreshold: number,
): T[] {
  const result: T[] = []
  const byClass = new Map<number, T[]>()

  for (const detection of detections) {
    const group = byClass.get(detection.classId) ?? []
    group.push(detection)
    byClass.set(detection.classId, group)
  }

  for (const group of byClass.values()) {
    const remaining = [...group].sort((a, b) => b.confidence - a.confidence)
    while (remaining.length > 0) {
      const best = remaining.shift()
      if (!best) {
        break
      }
      result.push(best)

      for (let index = remaining.length - 1; index >= 0; index -= 1) {
        if (boxIou(best.box, remaining[index]?.box) > iouThreshold) {
          remaining.splice(index, 1)
        }
      }
    }
  }

  return result
}

export function boxIou(
  a: DetectionBox,
  b: DetectionBox | undefined,
): number {
  if (!b) {
    return 0
  }

  const left = Math.max(a.x, b.x)
  const top = Math.max(a.y, b.y)
  const right = Math.min(a.x + a.width, b.x + b.width)
  const bottom = Math.min(a.y + a.height, b.y + b.height)

  const intersectionWidth = Math.max(0, right - left)
  const intersectionHeight = Math.max(0, bottom - top)
  const intersection = intersectionWidth * intersectionHeight
  const areaA = Math.max(0, a.width) * Math.max(0, a.height)
  const areaB = Math.max(0, b.width) * Math.max(0, b.height)
  const union = areaA + areaB - intersection

  return union > 0 ? intersection / union : 0
}

function reverseLetterbox(
  box: DetectionBox,
  transform: ImageTransform,
): DetectionBox {
  const x1 = clamp(
    (box.x - transform.padX) / transform.scale,
    0,
    transform.originalWidth,
  )
  const y1 = clamp(
    (box.y - transform.padY) / transform.scale,
    0,
    transform.originalHeight,
  )
  const x2 = clamp(
    (box.x + box.width - transform.padX) / transform.scale,
    0,
    transform.originalWidth,
  )
  const y2 = clamp(
    (box.y + box.height - transform.padY) / transform.scale,
    0,
    transform.originalHeight,
  )

  return {
    x: x1,
    y: y1,
    width: Math.max(0, x2 - x1),
    height: Math.max(0, y2 - y1),
  }
}

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.min(maximum, Math.max(minimum, value))
}
