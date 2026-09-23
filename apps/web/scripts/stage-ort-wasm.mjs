import { copyFile, mkdir, stat } from 'node:fs/promises'
import path from 'node:path'

const root = process.cwd()
const sourceDir = path.join(root, 'node_modules', 'onnxruntime-web', 'dist')
const targetDir = path.join(root, 'public', 'assets')

const files = [
  'ort-wasm-simd-threaded.mjs',
  'ort-wasm-simd-threaded.wasm',
]

await mkdir(targetDir, { recursive: true })

for (const name of files) {
  const source = path.join(sourceDir, name)
  const target = path.join(targetDir, name)
  const info = await stat(source)

  if (!info.isFile() || info.size <= 0) {
    throw new Error(`Invalid ONNX Runtime asset: ${source}`)
  }

  await copyFile(source, target)
  console.log(
    JSON.stringify({
      status: 'ORT_WASM_ASSET_STAGED',
      name,
      bytes: info.size,
      source,
      target,
    }),
  )
}
