// @vitest-environment jsdom

import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import App from '../src/App.vue'

const analyzeMock = vi.hoisted(() => vi.fn())

vi.mock('../src/ml/analysis', () => ({
  analyzeImageFile: analyzeMock,
}))

function attachImage(wrapper: ReturnType<typeof mount>): Promise<void> {
  const input = wrapper.get('[data-testid="image-input"]').element as HTMLInputElement
  const file = new File(['fake-image'], 'weld.jpg', { type: 'image/jpeg' })
  Object.defineProperty(input, 'files', {
    configurable: true,
    value: [file],
  })
  return wrapper.get('[data-testid="image-input"]').trigger('change')
}

beforeEach(() => {
  analyzeMock.mockReset()
  vi.stubGlobal('URL', {
    createObjectURL: vi.fn(() => 'blob:weld'),
    revokeObjectURL: vi.fn(),
  })
})

describe('B5 result semantics', () => {
  it('renders supported detections as educational indications', async () => {
    analyzeMock.mockResolvedValue({
      detections: [
        {
          classId: 1,
          label: 'spatter',
          confidence: 0.82,
          box: { x: 10, y: 10, width: 40, height: 20 },
        },
      ],
      imageWidth: 640,
      imageHeight: 480,
      provider: 'wasm',
      runtimeWarnings: [],
      modelId: 'weld-yolox-nano',
      modelVersion: '0.1.0',
      confidenceThreshold: 0.2,
    })

    const wrapper = mount(App)
    await attachImage(wrapper)
    await wrapper.get('button.primary').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Salpicadura')
    expect(wrapper.text()).toContain('Indicación potencial')
    expect(wrapper.text()).not.toContain('soldadura aprobada')
  })

  it('does not present zero detections as approval', async () => {
    analyzeMock.mockResolvedValue({
      detections: [],
      imageWidth: 640,
      imageHeight: 480,
      provider: 'wasm',
      runtimeWarnings: [],
      modelId: 'weld-yolox-nano',
      modelVersion: '0.1.0',
      confidenceThreshold: 0.2,
    })

    const wrapper = mount(App)
    await attachImage(wrapper)
    await wrapper.get('button.primary').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Sin detecciones soportadas')
    expect(wrapper.text()).toContain(
      'no significa que la soldadura sea aceptable, segura o libre de defectos',
    )
  })

  it('keeps runtime failure distinct from zero detections', async () => {
    analyzeMock.mockRejectedValue(new Error('Fallo controlado del runtime'))

    const wrapper = mount(App)
    await attachImage(wrapper)
    await wrapper.get('button.primary').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('No se pudo analizar la imagen')
    expect(wrapper.text()).toContain('Fallo controlado del runtime')
    expect(wrapper.text()).toContain(
      'no debe interpretarse como ausencia de anomalías',
    )
  })
})
