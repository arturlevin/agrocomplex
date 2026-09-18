import { defineStore } from 'pinia'
import http from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isChief: (state) => state.user?.role === 'chief_agronomist',
  },

  actions: {
    async login(email, password) {
      const form = new URLSearchParams()
      form.append('username', email)
      form.append('password', password)

      const { data } = await http.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })

      this.token = data.access_token
      localStorage.setItem('token', this.token)
      await this.fetchMe()
    },

    async fetchMe() {
      const { data } = await http.get('/auth/me')
      this.user = data
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    },
  },
})
