<template>
  <div class="unified-coderunner-container flex flex-col h-full border border-gray-300 rounded-lg shadow-sm bg-gray-50">
    <!-- Header Bar -->
    <div class="flex items-center justify-between px-4 py-2.5 bg-gray-100 border-b border-gray-300">
      <div class="flex items-center space-x-3">
        <span class="text-sm font-bold text-gray-800 tracking-tight">{{ problemTitle || 'Coding Challenge' }}</span>
        <span
          :class="['px-2 py-0.5 text-xs font-semibold rounded uppercase tracking-wider',
            mode === 'exam' ? 'bg-amber-100 text-amber-800 border border-amber-300' : 'bg-blue-100 text-blue-800']"
        >
          {{ mode === 'exam' ? 'Exam Mode (Proctored)' : 'Practice Mode' }}
        </span>
      </div>

      <!-- Proctoring Warnings (Exam Mode) -->
      <div v-if="mode === 'exam'" class="flex items-center space-x-4 text-xs">
        <div class="flex items-center space-x-1.5">
          <span class="text-gray-500">Tab Switches:</span>
          <span :class="['font-bold px-1.5 py-0.5 rounded', tabSwitches >= maxTabSwitches ? 'bg-rose-100 text-rose-700' : 'bg-gray-200 text-gray-800']">
            {{ tabSwitches }} / {{ maxTabSwitches }}
          </span>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center space-x-2">
        <button
          @click="runCode('practice_sample_only')"
          :disabled="isRunning"
          class="px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 shadow-sm disabled:opacity-50"
        >
          {{ isRunning ? 'Running...' : 'Run Code' }}
        </button>

        <button
          @click="submitSolution"
          :disabled="isRunning"
          class="px-4 py-1.5 text-xs font-bold text-white bg-blue-600 rounded hover:bg-blue-700 shadow-sm disabled:opacity-50"
        >
          {{ isRunning ? 'Evaluating...' : 'Submit' }}
        </button>
      </div>
    </div>

    <!-- Violation Alert Banner -->
    <div v-if="violationAlert" class="bg-rose-600 text-white px-4 py-1.5 text-xs font-semibold flex items-center justify-between animate-pulse">
      <span>{{ violationAlert }}</span>
    </div>

    <!-- Code Editor Section -->
    <div class="relative flex-1 min-h-[350px] bg-[#1e1e1e]">
      <textarea
        ref="editorArea"
        v-model="sourceCode"
        @copy.prevent="handleCopyPasteTrap"
        @paste.prevent="handleCopyPasteTrap"
        @contextmenu.prevent="handleContextMenuTrap"
        class="w-full h-full p-4 font-mono text-xs bg-[#1e1e1e] text-gray-100 border-none outline-none resize-none leading-relaxed"
        spellcheck="false"
      ></textarea>
    </div>

    <!-- Output Panel Component -->
    <OutputPanel :testcases="testcases" :result="executionResult" />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import OutputPanel from './OutputPanel.vue'

const props = defineProps({
  problemId: { type: String, required: true },
  problemTitle: { type: String, default: '' },
  language: { type: String, default: 'python' },
  initialCode: { type: String, default: '' },
  testcases: { type: Array, default: () => [] },
  mode: { type: String, default: 'practice' }, // 'practice' | 'exam'
  maxTabSwitches: { type: Number, default: 3 }
})

const emit = defineEmits(['submitted', 'autoSubmitted'])

const sourceCode = ref(props.initialCode || '')
const isRunning = ref(false)
const executionResult = ref(null)
const tabSwitches = ref(0)
const violationAlert = ref('')

// Client-Side Proctoring Handlers
const handleVisibilityChange = () => {
  if (props.mode !== 'exam') return

  if (document.hidden) {
    tabSwitches.value += 1
    violationAlert.value = `Tab switch detected! Warning (${tabSwitches.value}/${props.maxTabSwitches})`

    if (tabSwitches.value >= props.maxTabSwitches) {
      violationAlert.value = 'Maximum tab switches exceeded! Auto-submitting assessment...'
      autoSubmit()
    }
  }
}

const handleCopyPasteTrap = (e) => {
  if (props.mode === 'exam') {
    e.preventDefault()
    violationAlert.value = 'Copy / Paste is disabled during assessments!'
    setTimeout(() => { violationAlert.value = '' }, 3000)
  }
}

const handleContextMenuTrap = (e) => {
  if (props.mode === 'exam') {
    e.preventDefault()
  }
}

const runCode = async (evalMode = 'practice_sample_only') => {
  isRunning.value = true
  try {
    const response = await fetch('/api/method/coding_lms.api.evaluator.evaluate_code', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token || ''
      },
      body: JSON.stringify({
        problem_id: props.problemId,
        source_code: sourceCode.value,
        language: props.language,
        mode: evalMode
      })
    })

    const data = await response.json()
    executionResult.value = data.message || data
  } catch (err) {
    executionResult.value = {
      status: 'Error',
      error_message: 'Execution request failed. Check server connectivity.'
    }
  } finally {
    isRunning.value = false
  }
}

const submitSolution = async () => {
  await runCode(props.mode === 'exam' ? 'exam' : 'practice')
  emit('submitted', executionResult.value)
}

const autoSubmit = async () => {
  await submitSolution()
  emit('autoSubmitted', {
    tabSwitches: tabSwitches.value,
    result: executionResult.value
  })
}

onMounted(() => {
  if (props.mode === 'exam') {
    document.addEventListener('visibilitychange', handleVisibilityChange)
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>
