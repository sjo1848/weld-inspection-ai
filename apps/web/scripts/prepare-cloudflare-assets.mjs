import { createHash } from 'node:crypto'
import { mkdir, readdir, readFile, rename, rm, stat, writeFile } from 'node:fs/promises'
import path from 'node:path'

const root = process.cwd()
const dist = path.join(root, 'dist')
const stageRoot = path.join(root, '.deploy', 'r2')
const manifestPath = path.join(root, '.deploy', 'runtime-assets.json')
const staticLimit = 25 * 1024 * 1024

await rm(stageRoot, { recursive: true, force: true })
await mkdir(stageRoot, { recursive: true })

const files = await walk(dist)
const moved = []

for (const file of files) {
  const info = await stat(file)
  if (info.size <= staticLimit) continue

  const relative = path.relative(dist, file).split(path.sep).join('/')
  if (!relative.endsWith('.wasm')) {
    throw new Error(
      `Static asset exceeds 25 MiB and is not an approved WASM seam: ${relative} (${info.size} bytes)`,
    )
  }

  const destination = path.join(stageRoot, ...relative.split('/'))
  await mkdir(path.dirname(destination), { recursive: true })
  const sha256 = await sha256File(file)
  await rename(file, destination)

  moved.push({
    key: relative,
    bytes: info.size,
    sha256,
    stagedFile: path.relative(root, destination).split(path.sep).join('/'),
  })
}

if (moved.length === 0) {
  throw new Error('Expected at least one oversized ORT WASM asset to move to R2 staging.')
}

const remaining = await walk(dist)
for (const file of remaining) {
  const info = await stat(file)
  if (info.size > staticLimit) {
    throw new Error(
      `Static asset still exceeds Cloudflare 25 MiB limit: ${path.relative(dist, file)}`,
    )
  }
}

await mkdir(path.dirname(manifestPath), { recursive: true })
await writeFile(
  manifestPath,
  JSON.stringify(
    {
      stage: 'B6_RUNTIME_ASSET_SEAM_PREPARED',
      staticAssetLimitBytes: staticLimit,
      runtimeAssets: moved,
    },
    null,
    2,
  ) + '\n',
)

console.log(JSON.stringify({ manifestPath, moved }, null, 2))

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true })
  const result = []
  for (const entry of entries) {
    const full = path.join(directory, entry.name)
    if (entry.isDirectory()) result.push(...(await walk(full)))
    else if (entry.isFile()) result.push(full)
  }
  return result
}

async function sha256File(file) {
  const digest = createHash('sha256')
  digest.update(await readFile(file))
  return digest.digest('hex')
}
