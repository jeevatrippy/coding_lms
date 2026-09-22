<template>
  <div class="output-panel-container bg-white border border-gray-200 rounded-b-lg overflow-hidden flex flex-col font-sans">
    <!-- Tab Navigation -->
    <div class="flex items-center justify-between border-b border-gray-200 bg-gray-50 px-4 py-2">
      <div class="flex space-x-2">
        <button
          @click="activeTab = 'console'"
          :class="['px-3 py-1.5 text-xs font-semibold rounded-md transition-colors',
            activeTab === 'console' ? 'bg-white text-blue-600 shadow-sm border border-gray-200' : 'text-gray-600 hover:text-gray-900']"
        >
          Console Output
        </button>
        <button
          @click="activeTab = 'testcases'"
          :class="['px-3 py-1.5 text-xs font-semibold rounded-md transition-colors flex items-center gap-1.5',
            activeTab === 'testcases' ? 'bg-white text-blue-600 shadow-sm border border-gray-200' : 'text-gray-600 hover:text-gray-900']"
        >
          Test Cases
          <span v-if="testcases && testcases.length" class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded-full text-[10px]">
            {{ testcases.length }}
          </span>
        </button>
      </div>

      <div v-if="result" class="text-xs font-medium">
        <span v-if="result.status === 'Accepted'" class="text-emerald-600 font-bold">All Tests Passed</span>
        <span v-else class="text-rose-600 font-bold">{{ result.status }}</span>
      </div>
    </div>

    <!-- Panel Content -->
    <div class="p-4 max-h-[280px] overflow-y-auto">
      <!-- 1. Console Output View -->
      <div v-if="activeTab === 'console'">
        <div class="bg-[#1e1e1e] text-gray-200 p-3 rounded-lg font-mono text-xs leading-relaxed min-h-[140px] border border-[#333]">
          <div v-if="result && result.error_message" class="text-rose-400 whitespace-pre-wrap">
            {{ result.error_message }}
          </div>
          <div v-else-if="result && result.status" class="whitespace-pre-wrap">
            Program execution completed. Status: {{ result.status }}
          </div>
          <div v-else class="text-gray-500 italic text-center py-10">
            Run your code to view terminal output and logs...
          </div>
        </div>
      </div>

      <!-- 2. Test Cases View -->
      <div v-if="activeTab === 'testcases'" class="space-y-3">
        <!-- Result Summary Banner -->
        <div
          v-if="result"
          :class="['p-3 rounded-lg border flex items-center justify-between text-xs',
            result.passed_count === result.total_testcases ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800']"
        >
          <span class="font-bold">Test Result Summary</span>
          <span>Passed: <strong>{{ result.passed_count }}</strong> / {{ result.total_testcases }}</span>
        </div>

        <!-- Before Run: Show Available Public Test Cases -->
        <div v-if="!result && testcases && testcases.length" class="space-y-2.5">
          <div
            v-for="(tc, i) in publicTestcases"
            :key="i"
            class="p-3 rounded-lg border bg-gray-50/70 border-gray-200 text-xs"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="font-bold text-gray-700 uppercase tracking-wide">Test Case {{ i + 1 }}</span>
              <span class="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-[10px] font-semibold">Public</span>
            </div>
            <div class="grid grid-cols-[60px_1fr] gap-y-1.5 font-mono">
              <span class="text-gray-400">Input:</span>
              <div class="bg-white px-2 py-1 rounded border border-gray-200 text-gray-800">{{ tc.input || "(Empty Input)" }}</div>
              <span class="text-gray-400">Expected:</span>
              <div class="bg-white px-2 py-1 rounded border border-gray-200 text-gray-800">{{ tc.expected_output }}</div>
            </div>
          </div>
        </div>

        <!-- After Run: Show Executed Results -->
        <div v-if="result && result.testcases" class="space-y-2.5">
          <div
            v-for="(tc, i) in result.testcases"
            :key="i"
            :class="['p-3 rounded-lg border text-xs',
              tc.status === 'passed' ? 'bg-emerald-50/40 border-emerald-200' : 'bg-rose-50/40 border-rose-200']"
          >
            <div class="flex items-center justify-between mb-2">
              <span :class="['font-bold uppercase tracking-wide', tc.status === 'passed' ? 'text-emerald-700' : 'text-rose-700']">
                {{ tc.description || ('Test Case ' + (i + 1)) }}
              </span>
              <div class="flex items-center gap-1.5">
                <span v-if="tc.is_public" class="bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded text-[10px]">Public</span>
                <span
                  :class="['px-2 py-0.5 rounded text-[10px] font-bold',
                    tc.status === 'passed' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800']"
                >
                  {{ tc.status === 'passed' ? 'Passed' : 'Failed' }}
                </span>
              </div>
            </div>

            <div class="grid grid-cols-[60px_1fr] gap-y-1.5 font-mono">
              <span class="text-gray-500">Input:</span>
              <div class="bg-white px-2 py-1 rounded border border-gray-200 text-gray-800">{{ tc.input }}</div>

              <span class="text-gray-500">Expected:</span>
              <div class="bg-white px-2 py-1 rounded border border-gray-200 text-gray-800">{{ tc.expected_output }}</div>

              <template v-if="tc.status !== 'passed'">
                <span class="text-rose-500 font-bold">Actual:</span>
                <div class="bg-rose-100/70 text-rose-900 px-2 py-1 rounded border border-rose-200">{{ tc.actual_output }}</div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  testcases: { type: Array, default: () => [] },
  result: { type: Object, default: null }
})

const activeTab = ref('testcases')

const publicTestcases = computed(() => {
  return props.testcases.filter(tc => tc.is_public)
})
</script>
