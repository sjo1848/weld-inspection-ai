export interface ImageTransform {
  originalWidth: number
  originalHeight: number
  inputWidth: number
  inputHeight: number
  resizedWidth: number
  resizedHeight: number
  scale: number
  padX: 0
  padY: 0
}

export interface PreprocessedImage {
  data: Float32Array
  transform: ImageTransform
}

export function computeTopLeftLetterbox(
  originalWidth: number,
  originalHeight: number,
  inputWidth = 416,
  inputHeight = 416,
): ImageTransform {
  if (originalWidth <= 0 || originalHeight <= 0) {
    throw new Error('Las dimensiones de imagen deben ser positivas.')
  }

  const scale = Math.min(
    inputHeight / originalHeight,
    inputWidth / originalWidth,
  )

  return {
    originalWidth,
    originalHeight,
    inputWidth,
    inputHeight,
    resizedWidth: Math.trunc(originalWidth * scale),
    resizedHeight: Math.trunc(originalHeight * scale),
    scale,
    padX: 0,
    padY: 0,
  }
}

export function rgbaToBgrNchw(
  rgba: Uint8ClampedArray,
  width: number,
  height: number,
): Float32Array {
  if (rgba.length !== width * height * 4) {
    throw new Error('El buffer RGBA no coincide con sus dimensiones.')
  }

  const plane = width * height
  const output = new Float32Array(plane * 3)

  for (let pixel = 0; pixel < plane; pixel += 1) {
    const source = pixel * 4
    output[pixel] = rgba[source + 2] ?? 0
    output[plane + pixel] = rgba[source + 1] ?? 0
    output[2 * plane + pixel] = rgba[source] ?? 0
  }

  return output
}

export function preprocessCanvasSource(
  source: CanvasImageSource,
  originalWidth: number,
  originalHeight: number,
  inputWidth = 416,
  inputHeight = 416,
): PreprocessedImage {
  const transform = computeTopLeftLetterbox(
    originalWidth,
    originalHeight,
    inputWidth,
    inputHeight,
  )

  const canvas = document.createElement('canvas')
  canvas.width = inputWidth
  canvas.height = inputHeight
  const context = canvas.getContext('2d', { willReadFrequently: true })
  if (!context) {
    throw new Error('No se pudo crear el contexto 2D para preprocesar la imagen.')
  }

  context.fillStyle = 'rgb(114, 114, 114)'
  context.fillRect(0, 0, inputWidth, inputHeight)
  context.imageSmoothingEnabled = true
  context.drawImage(
    source,
    0,
    0,
    transform.resizedWidth,
    transform.resizedHeight,
  )

  const rgba = context.getImageData(0, 0, inputWidth, inputHeight).data
  return {
    data: rgbaToBgrNchw(rgba, inputWidth, inputHeight),
    transform,
  }
}
