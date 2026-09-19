import { readFile } from 'node:fs/promises'
import { spawnSync } from 'node:child_process'
import path from 'node:path'

const root = process.cwd()
const bucket = process.env.WELD_VISION_R2_BUCKET ?? 'weld-vision-runtime'
const payload = JSON.parse(
  await readFile(path.join(root, '.deploy', 'runtime-assets.json'), 'utf8'),
)

for (const asset of payload.runtimeAssets) {
  const objectPath = `${bucket}/${asset.key}`
  const file = path.join(root, asset.stagedFile)
  const args = [
    'exec',
    'wrangler',
    'r2',
    'object',
    'put',
    objectPath,
    '--file',
    file,
    '--content-type',
    'application/wasm',
    '--cache-control',
    'public, max-age=31536000, immutable',
    '--remote',
  ]

  console.log('+ pnpm', args.join(' '))
  const result = spawnSync('pnpm', args, { stdio: 'inherit' })
  if (result.status !== 0) {
    process.exit(result.status ?? 1)
  }
}
