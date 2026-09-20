import { createHash } from 'node:crypto'
import { mkdir, readdir, readFile, stat, writeFile } from 'node:fs/promises'
import path from 'node:path'

const root = process.cwd()
const dist = path.join(root, 'dist')
const manifestPath = path.join(root, '.deploy', 'static-assets.json')
const staticLimit = 25 * 1024 * 1024

const files = await walk(dist)
const assets = []

for (const file of files) {
  const info = await stat(file)
  const relative = path.relative(dist, file).split(path.sep).join('/')
  const sha256 = await sha256File(file)

  assets.push({
    path: relative,
    bytes: info.size,
    sha256,
  })

  if (info.size > staticLimit) {
    throw new Error(
      `Static asset exceeds Cloudflare 25 MiB limit: ${relative} (${info.size} bytes)`,
    )
  }
}

assets.sort((a, b) => b.bytes - a.bytes)

await mkdir(path.dirname(manifestPath), { recursive: true })
await writeFile(
  manifestPath,
  JSON.stringify(
    {
      stage: 'B6_STATIC_ASSETS_VERIFIED',
      staticAssetLimitBytes: staticLimit,
      largestAsset: assets[0] ?? null,
      assets,
    },
    null,
    2,
  ) + '\n',
)

console.log(
  JSON.stringify(
    {
      manifestPath,
      assetCount: assets.length,
      largestAsset: assets[0] ?? null,
      status: 'PASS',
    },
    null,
    2,
  ),
)

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
