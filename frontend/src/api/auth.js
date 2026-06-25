import axios from 'axios'

const api = axios.create({
    baseURL: 'http://localhost:8000',
})

export async function login(username, email,password) {
    const response = await api.post('/api/accounts/login/', {
    username,
    email,
    password,
    })
    return response.data
}