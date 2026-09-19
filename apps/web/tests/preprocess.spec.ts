import { describe, expect, it } from 'vitest'

import { computeTopLeftLetterbox, rgbaToBgrNchw } from '../src/ml/preprocess'

describe('YOLOX preprocessing contract', () => {
  it('uses top-left letterbox geometry for landscape images', () => {
    const transform = computeTopLeftLetterbox(832, 416)
    expect(transform.scale).toBe(0.5)
    expect(transform.resizedWidth).toBe(416)
    expect(transform.resizedHeight).toBe(208)
    expect(transform.padX).toBe(0)
    expect(transform.padY).toBe(0)
  })

  it('uses Python-style truncation for portrait resize dimensions', () => {
    const transform = computeTopLeftLetterbox(301, 503)
    expect(transform.resizedHeight).toBe(416)
    expect(transform.resizedWidth).toBe(Math.trunc(301 * (416 / 503)))
  })

  it('converts RGBA canvas pixels to BGR NCHW without normalization', () => {
    const rgba = new Uint8ClampedArray([
      10, 20, 30, 255,
      40, 50, 60, 255,
    ])
    const tensor = rgbaToBgrNchw(rgba, 2, 1)
    expect(Array.from(tensor)).toEqual([
      30, 60,
      20, 50,
      10, 40,
    ])
  })
})
