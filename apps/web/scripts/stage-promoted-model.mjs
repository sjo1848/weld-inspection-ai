import { createHash } from 'node:crypto'
import { copyFile, mkdir, readFile, stat } from 'node:fs/promises'
import path from 'node:path'

const expectedSha =
  'b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714'
const expectedBytes = 3653900
const source = process.env.WELD_VISION_MODEL_PATH

if (!source) {
  throw new Error('WELD_VISION_MODEL_PATH must point to the promoted B4 ONNX file.')
}

const bytes = (await stat(source)).size
if (bytes !== expectedBytes) {
  throw new Error(`Promoted model byte-size mismatch: ${bytes} != ${expectedBytes}`)
}

const sha = createHash('sha256').update(await readFile(source)).digest('hex')
if (sha !== expectedSha) {
  throw new Error(`Promoted model SHA-256 mismatch: ${sha} != ${expectedSha}`)
}

const destination = path.join(
  process.cwd(),
  'public',
  'models',
  'weld-yolox-nano-v0.1.onnx',
)
await mkdir(path.dirname(destination), { recursive: true })
await copyFile(source, destination)

console.log(
  JSON.stringify(
    {
      status: 'PROMOTED_MODEL_STAGED',
      source,
      destination,
      bytes,
      sha256: sha,
    },
    null,
    2,
  ),
)
