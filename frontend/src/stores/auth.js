import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi} from '../api/auth'

export const useAuthStore = defineStore('auth',() =>{
    const token = ref(localStorage.getItem('access_token') || null)
    const user = ref(null)

async function login(username, email, password) {
    const data = await loginApi(username, email, password)
    token.value = data.access
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
}

    function logout() {
        token.value = null
        user.value = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
    }

    const isAuthenticated = () => !!token.value

    return {
        token,
        user,
        login,
        logout,
        isAuthenticated,
    }
})


