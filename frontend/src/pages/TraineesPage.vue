<template>
  <div>
    <div class="mb-6">
        <h2 class="text-2xl font-bold text-gray-800">研修生一覧</h2>
        <p class="text-sm text-gray-500 mt-1">登録中の研修生の進捗とステータスを管理します</p>
    </div>

    <div v-if="loading" class="flex justify-center items-center py-20">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4">
        <p class="font-medium">データの取得に失敗しました</p>
        <p class="text-sm mt-1">{{ error }}</p>
        <button @click="fetchTrainees" class="mt-3 text-sm underline hover:no-underline">再試行する</button>
    </div>

    <div v-else class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div class="flex items-center gap-6 px-6 py-4 border-b border-gray-100 bg-gray-50">
            <span class="text-sm text-gray-600">
                合計 <span class="font-semibold text-gray-800">{{ trainees.length }}</span> 名
            </span>
            <span class="text-sm text-red-600" v-if="delayedCount > 0">
                ⚠ 遅延 <span class="font-semibold">{{ delayedCount }}</span> 名
            </span>
            <span class="text-sm text-green-600" v-if="completedCount > 0">
                ✓ 完了 <span class="font-semibold">{{ completedCount }}</span> 名
            </span>
        </div>

        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead>
                    <tr class="border-b border-gray-200 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    <th class="px-6 py-3">名前</th>
                    <th class="px-6 py-3">メール</th>
                    <th class="px-6 py-3">進捗</th>
                    <th class="px-6 py-3">ステータス</th>
                    <th class="px-6 py-3">遅延</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                    <tr
                    v-for="trainee in trainees"
                    :key="trainee.id"
                    :class="[
                        'hover:bg-gray-50 transition-colors',
                        trainee.is_delayed ? 'bg-red-50 hover:bg-red-100' : ''
                    ]"
                    >
              <td class="px-6 py-4">
                <div class="font-medium text-gray-800">{{ trainee.full_name || trainee.username }}</div>
                <div class="text-xs text-gray-400">{{ trainee.username }}</div>
              </td>
              <td class="px-6 py-4 text-gray-600">{{ trainee.email }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-3 min-w-[140px]">
                  <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all"
                      :class="progressBarColor(trainee)"
                      :style="{ width: trainee.overall_progress_percent + '%' }"
                    ></div>
                  </div>
                  <span class="text-xs font-medium text-gray-600 w-8 text-right">{{ trainee.overall_progress_percent }}%</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <span :class="['inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', statusBadgeClass(trainee.status)]">
                  {{ statusLabel(trainee.status) }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span v-if="trainee.is_delayed" class="text-red-500 font-medium text-xs">⚠ 遅延</span>
                <span v-else class="text-gray-300 text-xs">—</span>
              </td>
            </tr>
            <tr v-if="trainees.length === 0">
              <td colspan="5" class="px-6 py-16 text-center text-gray-400">研修生が登録されていません</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import apiClient from '@/api/client.js'

const trainees = ref([])
const loading = ref(false)
const error = ref(null)

const fetchTrainees = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await apiClient.get('/api/trainees/')
    trainees.value = Array.isArray(response.data) ? response.data : (response.data.results ?? [])
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || '不明なエラー'
  } finally {
    loading.value = false
  }
}

onMounted(fetchTrainees)

const delayedCount = computed(() => trainees.value.filter(t => t.is_delayed).length)
const completedCount = computed(() => trainees.value.filter(t => t.status === 'completed').length)

const progressBarColor = (trainee) => {
  if (trainee.is_delayed) return 'bg-red-400'
  if (trainee.overall_progress_percent >= 100) return 'bg-green-500'
  if (trainee.overall_progress_percent >= 50) return 'bg-blue-500'
  return 'bg-blue-400'
}

const statusLabel = (status) => {
  const map = {
    active: '進行中',
    completed: '完了',
    suspended: '停止中',
    not_started: '未開始',
  }
  return map[status] ?? status
}

const statusBadgeClass = (status) => {
  const map = {
    active: 'bg-blue-100 text-blue-700',
    completed: 'bg-green-100 text-green-700',
    suspended: 'bg-gray-100 text-gray-600',
    not_started: 'bg-yellow-100 text-yellow-700',
  }
  return map[status] ?? 'bg-gray-100 text-gray-600'
}
</script>
