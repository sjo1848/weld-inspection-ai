import { describe, expect, it } from 'vitest'

import type { ModelManifest } from '../src/ml/manifest'
import type { ImageTransform } from '../src/ml/preprocess'
import {
  boxIou,
  classAwareNms,
  decodeYoloxRaw,
  type WeldDetection,
} from '../src/ml/yolox'

const manifest: ModelManifest = {
  stage: 'B4_PROMOTED_MODEL_V0_1',
  modelId: 'weld-yolox-nano',
  modelVersion: '0.1.0',
  artifactPath: '/models/weld-yolox-nano-v0.1.onnx',
  artifactSha256: 'x',
  artifactBytes: 1,
  inputWidth: 416,
  inputHeight: 416,
  inputTensorName: 'images',
  inputDtype: 'float32',
  inputLayout: 'NCHW',
  outputTensorNames: ['output'],
  outputTensorShapes: { output: [1, 3549, 8] },
  rawOutputDecodedInModel: false,
  classMap: {
    '0': 'slag inclusion',
    '1': 'spatter',
    '2': 'undercut',
  },
  supportedClasses: ['spatter', 'slag inclusion'],
  diagnosticOnlyClasses: ['undercut'],
  confidenceThreshold: 0.2,
  nmsThreshold: 0.65,
  preprocessingVersion: 'yolox-val-416-v1',
  postprocessingVersion: 'yolox-raw-adapter-v1',
  toolingCommit: 'test',
  limitations: [],
}

const transform: ImageTransform = {
  originalWidth: 832,
  originalHeight: 416,
  inputWidth: 416,
  inputHeight: 416,
  resizedWidth: 416,
  resizedHeight: 208,
  scale: 0.5,
  padX: 0,
  padY: 0,
}

describe('YOLOX raw adapter', () => {
  it('decodes a supported class and reverses the letterbox scale', () => {
    const raw = new Float32Array(3549 * 8)
    raw[4] = 0.9
    raw[6] = 0.8

    const detections = decodeYoloxRaw(raw, transform, manifest)

    expect(detections).toHaveLength(1)
    expect(detections[0]?.label).toBe('spatter')
    expect(detections[0]?.confidence).toBeCloseTo(0.72)
    expect(detections[0]?.box.width).toBeCloseTo(16)
    expect(detections[0]?.box.height).toBeCloseTo(16)
  })

  it('does not relabel diagnostic-only undercut as a supported class', () => {
    const raw = new Float32Array(3549 * 8)
    raw[4] = 0.95
    raw[5] = 0.7
    raw[6] = 0.8
    raw[7] = 0.9

    expect(decodeYoloxRaw(raw, transform, manifest)).toEqual([])
  })

  it('performs class-aware NMS', () => {
    const base: WeldDetection = {
      classId: 1,
      label: 'spatter',
      confidence: 0.9,
      box: { x: 10, y: 10, width: 100, height: 100 },
    }
    const overlapping: WeldDetection = {
      ...base,
      confidence: 0.8,
      box: { x: 12, y: 12, width: 100, height: 100 },
    }
    const otherClass: WeldDetection = {
      ...base,
      classId: 0,
      label: 'slag inclusion',
      confidence: 0.7,
    }

    const kept = classAwareNms([base, overlapping, otherClass], 0.65)
    expect(kept).toHaveLength(2)
    expect(kept).toContain(base)
    expect(kept).toContain(otherClass)
    expect(boxIou(base.box, overlapping.box)).toBeGreaterThan(0.65)
  })
})
