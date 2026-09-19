export default {
  async fetch(request, env) {
    const url = new URL(request.url)

    if (url.pathname.startsWith('/assets/') && url.pathname.endsWith('.wasm')) {
      const key = url.pathname.slice(1)
      const object = await env.RUNTIME_BUCKET.get(key)

      if (object) {
        const headers = new Headers()
        object.writeHttpMetadata?.(headers)
        headers.set('content-type', 'application/wasm')
        headers.set('cache-control', 'public, max-age=31536000, immutable')
        if (object.httpEtag) {
          headers.set('etag', object.httpEtag)
        }
        return new Response(object.body, { headers })
      }
    }

    return env.ASSETS.fetch(request)
  },
}
