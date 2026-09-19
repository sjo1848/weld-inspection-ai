<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'

import { analyzeImageFile, type AnalysisResult } from './ml/analysis'

type Phase = 'idle' | 'ready' | 'analyzing' | 'result' | 'error'

const phase = ref<Phase>('idle')
const selectedFile = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const result = ref<AnalysisResult | null>(null)
const errorMessage = ref<string | null>(null)

const isBusy = computed(() => phase.value === 'analyzing')
const canAnalyze = computed(
  () => selectedFile.value !== null && !isBusy.value,
)

const resultSummary = computed(() => {
  const detections = result.value?.detections ?? []
  if (detections.length === 0) {
    return 'No se detectaron anomalías soportadas por encima del umbral configurado.'
  }

  const spatter = detections.filter((item) => item.label === 'spatter').length
  const slag = detections.filter(
    (item) => item.label === 'slag inclusion',
  ).length
  const parts: string[] = []
  if (spatter > 0) {
    parts.push(`${spatter} indicación(es) de salpicadura`)
  }
  if (slag > 0) {
    parts.push(`${slag} indicación(es) de inclusión visible de escoria`)
  }
  return parts.join(' · ')
})

function handleFileChange(event: Event): void {
  const input = event.currentTarget as HTMLInputElement
  const file = input.files?.[0]
  if (!file) {
    return
  }

  replacePreview(file)
  selectedFile.value = file
  result.value = null
  errorMessage.value = null
  phase.value = 'ready'
}

async function runAnalysis(): Promise<void> {
  const file = selectedFile.value
  if (!file) {
    return
  }

  phase.value = 'analyzing'
  result.value = null
  errorMessage.value = null

  try {
    result.value = await analyzeImageFile(file)
    phase.value = 'result'
  } catch (error) {
    errorMessage.value =
      error instanceof Error
        ? error.message
        : 'No se pudo completar el análisis.'
    phase.value = 'error'
  }
}

function startNewAnalysis(): void {
  selectedFile.value = null
  result.value = null
  errorMessage.value = null
  phase.value = 'idle'
  clearPreview()
}

function replacePreview(file: File): void {
  clearPreview()
  previewUrl.value = URL.createObjectURL(file)
}

function clearPreview(): void {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = null
  }
}

function detectionName(label: string): string {
  if (label === 'spatter') {
    return 'Salpicadura'
  }
  if (label === 'slag inclusion') {
    return 'Inclusión visible de escoria'
  }
  return label
}

onBeforeUnmount(clearPreview)
</script>

<template>
  <main class="shell">
    <header class="hero">
      <span class="eyebrow">Prototipo educativo · análisis local</span>
      <h1>Asistente visual de soldadura</h1>
      <p class="lead">
        Detecta indicaciones potenciales de salpicadura e inclusión visible de
        escoria en fotografías de soldaduras SMAW.
      </p>
      <p class="boundary">
        No certifica, aprueba ni rechaza una soldadura. No reemplaza inspección
        profesional ni ensayos no destructivos.
      </p>
    </header>

    <section class="card" aria-labelledby="input-title">
      <div class="section-heading">
        <div>
          <span class="step">1</span>
          <div>
            <h2 id="input-title">Elegí una fotografía</h2>
            <p>La imagen se procesa en este navegador.</p>
          </div>
        </div>
      </div>

      <label class="picker">
        <input
          data-testid="image-input"
          type="file"
          accept="image/*"
          capture="environment"
          @change="handleFileChange"
        />
        <span>{{ selectedFile ? 'Cambiar imagen' : 'Tomar o elegir foto' }}</span>
      </label>

      <p v-if="selectedFile" class="file-meta">
        {{ selectedFile.name }} · {{ (selectedFile.size / 1024 / 1024).toFixed(2) }} MB
      </p>
    </section>

    <section v-if="previewUrl" class="card" aria-labelledby="preview-title">
      <div class="section-heading">
        <div>
          <span class="step">2</span>
          <div>
            <h2 id="preview-title">Vista previa</h2>
            <p>Revisá que el cordón sea visible antes de analizar.</p>
          </div>
        </div>
      </div>

      <div class="preview-frame">
        <img :src="previewUrl" alt="Fotografía de soldadura seleccionada" />
        <svg
          v-if="result && result.detections.length > 0"
          class="overlay"
          :viewBox="`0 0 ${result.imageWidth} ${result.imageHeight}`"
          preserveAspectRatio="xMidYMid meet"
          aria-label="Anomalías potenciales localizadas"
        >
          <rect
            v-for="(detection, index) in result.detections"
            :key="`${detection.classId}-${index}`"
            :x="detection.box.x"
            :y="detection.box.y"
            :width="detection.box.width"
            :height="detection.box.height"
            class="detection-box"
          />
        </svg>
      </div>

      <button
        class="primary"
        type="button"
        :disabled="!canAnalyze"
        @click="runAnalysis"
      >
        {{ isBusy ? 'Analizando en el dispositivo…' : 'Analizar fotografía' }}
      </button>
    </section>

    <section
      v-if="phase === 'result' && result"
      class="card result-card"
      data-testid="result-card"
      aria-live="polite"
    >
      <div class="section-heading">
        <div>
          <span class="step">3</span>
          <div>
            <h2>Resultado educativo</h2>
            <p>{{ resultSummary }}</p>
          </div>
        </div>
      </div>

      <div
        v-if="result.detections.length === 0"
        class="notice neutral"
        data-testid="zero-result"
      >
        <strong>Sin detecciones soportadas.</strong>
        <p>
          Esto no significa que la soldadura sea aceptable, segura o libre de
          defectos. El modelo sólo busca las clases soportadas y puede omitir
          anomalías visibles.
        </p>
      </div>

      <ul v-else class="detection-list">
        <li
          v-for="(detection, index) in result.detections"
          :key="`result-${detection.classId}-${index}`"
          data-testid="detection-item"
        >
          <div>
            <strong>{{ detectionName(detection.label) }}</strong>
            <span>Indicación potencial</span>
          </div>
          <b>{{ (detection.confidence * 100).toFixed(0) }}%</b>
        </li>
      </ul>

      <div class="runtime" data-testid="runtime-info">
        <span>Modelo {{ result.modelVersion }}</span>
        <span>Runtime {{ result.provider.toUpperCase() }}</span>
        <span>Umbral {{ result.confidenceThreshold.toFixed(2) }}</span>
      </div>

      <p
        v-for="warning in result.runtimeWarnings"
        :key="warning"
        class="runtime-warning"
      >
        {{ warning }}
      </p>

      <button class="secondary" type="button" @click="startNewAnalysis">
        Nueva fotografía
      </button>
    </section>

    <section
      v-if="phase === 'error'"
      class="card error-card"
      data-testid="runtime-error"
      aria-live="assertive"
    >
      <h2>No se pudo analizar la imagen</h2>
      <p>{{ errorMessage }}</p>
      <p>
        Este es un error de ejecución; no debe interpretarse como ausencia de
        anomalías.
      </p>
      <button class="secondary" type="button" @click="runAnalysis">
        Reintentar
      </button>
    </section>

    <footer>
      <strong>Clases soportadas v0.1:</strong>
      salpicadura e inclusión visible de escoria.
      <span>Undercut no está promovida como clase soportada.</span>
    </footer>
  </main>
</template>

<style>
:root {
  color: #17211d;
  background: #edf1ee;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
  font-synthesis: none;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
}

button,
input {
  font: inherit;
}

.shell {
  width: min(100%, 760px);
  margin: 0 auto;
  padding: 28px 16px 48px;
}

.hero {
  padding: 10px 2px 22px;
}

.eyebrow {
  display: inline-block;
  margin-bottom: 10px;
  color: #35604f;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1,
h2,
p {
  margin-top: 0;
}

h1 {
  margin-bottom: 12px;
  font-size: clamp(2rem, 8vw, 3.6rem);
  line-height: 0.98;
  letter-spacing: -0.045em;
}

.lead {
  max-width: 650px;
  margin-bottom: 12px;
  color: #405049;
  font-size: 1.06rem;
  line-height: 1.55;
}

.boundary {
  margin: 0;
  padding-left: 12px;
  border-left: 3px solid #a66532;
  color: #5b4b3e;
  font-size: 0.9rem;
  line-height: 1.45;
}

.card {
  margin-top: 14px;
  padding: 18px;
  border: 1px solid #d1d9d4;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 8px 28px rgb(22 36 29 / 6%);
}

.section-heading > div {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.section-heading h2 {
  margin-bottom: 4px;
  font-size: 1.08rem;
}

.section-heading p {
  margin-bottom: 0;
  color: #64736c;
  font-size: 0.88rem;
  line-height: 1.4;
}

.step {
  display: grid;
  width: 30px;
  height: 30px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 50%;
  background: #173b2f;
  color: #fff;
  font-size: 0.82rem;
  font-weight: 800;
}

.picker {
  display: flex;
  min-height: 52px;
  align-items: center;
  justify-content: center;
  margin-top: 18px;
  padding: 12px 18px;
  border: 1px dashed #789487;
  border-radius: 13px;
  background: #f5f8f6;
  color: #24483a;
  cursor: pointer;
  font-weight: 750;
}

.picker input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
}

.file-meta {
  margin: 10px 0 0;
  color: #6d7772;
  font-size: 0.78rem;
  text-align: center;
}

.preview-frame {
  position: relative;
  overflow: hidden;
  margin-top: 16px;
  border-radius: 14px;
  background: #111;
}

.preview-frame img {
  display: block;
  width: 100%;
  max-height: 62vh;
  object-fit: contain;
}

.overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.detection-box {
  fill: transparent;
  stroke: #f5b23c;
  stroke-width: 3;
  vector-effect: non-scaling-stroke;
}

.primary,
.secondary {
  width: 100%;
  min-height: 50px;
  margin-top: 16px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
}

.primary {
  border: 0;
  background: #173b2f;
  color: white;
}

.primary:disabled {
  cursor: wait;
  opacity: 0.58;
}

.secondary {
  border: 1px solid #aebbb4;
  background: #fff;
  color: #253c33;
}

.result-card {
  border-color: #b8cbc0;
}

.notice {
  margin-top: 16px;
  padding: 14px;
  border-radius: 12px;
}

.notice p {
  margin: 6px 0 0;
  line-height: 1.45;
}

.notice.neutral {
  background: #f0f4f1;
}

.detection-list {
  display: grid;
  gap: 8px;
  margin: 16px 0 0;
  padding: 0;
  list-style: none;
}

.detection-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #f4f6f4;
}

.detection-list li div {
  display: grid;
  gap: 2px;
}

.detection-list span {
  color: #68756f;
  font-size: 0.78rem;
}

.runtime {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 14px;
}

.runtime span {
  padding: 5px 8px;
  border-radius: 999px;
  background: #e9eeeb;
  color: #4d5f56;
  font-size: 0.72rem;
  font-weight: 700;
}

.runtime-warning {
  margin: 10px 0 0;
  color: #70552c;
  font-size: 0.8rem;
}

.error-card {
  border-color: #d6b3ad;
  background: #fff9f8;
}

.error-card h2 {
  color: #7a3028;
}

.error-card p {
  color: #62443f;
  line-height: 1.45;
}

footer {
  display: grid;
  gap: 4px;
  padding: 22px 4px 0;
  color: #637069;
  font-size: 0.76rem;
  line-height: 1.4;
}

@media (min-width: 680px) {
  .shell {
    padding-top: 54px;
  }

  .card {
    padding: 24px;
  }
}
</style>
