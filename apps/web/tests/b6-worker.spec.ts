import { describe, expect, it, vi } from 'vitest'

import worker from '../worker/index.js'

describe('B6 Cloudflare runtime asset seam', () => {
  it('streams a WASM asset from R2 with immutable cache headers', async () => {
    const body = new Uint8Array([0, 97, 115, 109])
    const get = vi.fn(async (key) => ({
      body,
      httpEtag: '"runtime-etag"',
      writeHttpMetadata(headers) {
        headers.set('x-test-metadata', 'present')
      },
    }))
    const assetsFetch = vi.fn()

    const response = await worker.fetch(
      new Request('https://example.test/assets/runtime.wasm'),
      {
        RUNTIME_BUCKET: { get },
        ASSETS: { fetch: assetsFetch },
      },
    )

    expect(get).toHaveBeenCalledWith('assets/runtime.wasm')
    expect(assetsFetch).not.toHaveBeenCalled()
    expect(response.headers.get('content-type')).toBe('application/wasm')
    expect(response.headers.get('cache-control')).toContain('immutable')
    expect(response.headers.get('etag')).toBe('"runtime-etag"')
    expect(new Uint8Array(await response.arrayBuffer())).toEqual(body)
  })

  it('falls through to Static Assets when R2 has no matching object', async () => {
    const get = vi.fn(async () => null)
    const assetsFetch = vi.fn(async () => new Response('asset fallback'))

    const response = await worker.fetch(
      new Request('https://example.test/assets/other.wasm'),
      {
        RUNTIME_BUCKET: { get },
        ASSETS: { fetch: assetsFetch },
      },
    )

    expect(assetsFetch).toHaveBeenCalledOnce()
    expect(await response.text()).toBe('asset fallback')
  })

  it('does not query R2 for ordinary application assets', async () => {
    const get = vi.fn()
    const assetsFetch = vi.fn(async () => new Response('index'))

    await worker.fetch(new Request('https://example.test/'), {
      RUNTIME_BUCKET: { get },
      ASSETS: { fetch: assetsFetch },
    })

    expect(get).not.toHaveBeenCalled()
    expect(assetsFetch).toHaveBeenCalledOnce()
  })
})
