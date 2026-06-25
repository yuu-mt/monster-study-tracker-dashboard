<template>
    <div class="min-h-screen bg-gray-100 flex items-center justify-center">
        <div class="bg-white rounded-2xl shadow-md p-8 w-full max-w-sm">
        <h1 class="text-2xl font-bold text-gray-800 mb-2">Monster Study Tracker</h1>
        <p class="text-sm text-gray-500 mb-6">講師ダッシュボード</p>

        <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {{ errorMessage }}
        </div>

        <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">ユーザー名</label>
            <input
            v-model="username"
            type="text"
            placeholder="username"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
        </div>

        <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">メールアドレス</label>
            <input
                v-model="email"
                type="email"
                placeholder="example@example.com"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
        </div>

        <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-1">パスワード</label>
            <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
        </div>

        <button
            @click="handleLogin"
            :disabled="isLoading"
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-2 rounded-lg text-sm transition-colors"
        >
            {{ isLoading ? 'ログイン中...' : 'ログイン' }}
        </button>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMessage = ref('')


async function handleLogin() {
    console.log('handleLogin called')
    console.log('username:', username.value, 'email:', email.value, 'password:', password.value)
    if (!username.value || !email.value || !password.value) {
        errorMessage.value = 'すべての項目を入力してください'
        return
    }

    isLoading.value = true
    errorMessage.value = ''

    try {
        await auth.login(username.value, email.value, password.value)
        router.push('/dashboard')
    } catch (e) {
        console.log('error:', e)
        errorMessage.value = 'ユーザー名またはパスワードが正しくありません'
    } finally {
        isLoading.value = false
    }
}

</script>