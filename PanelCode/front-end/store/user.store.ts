export default defineStore('user', {
  state: () => ({
    username: '',
    password: '',
    isLoggedIn: false
  }),
  actions: {
    async login(username: string, password: string) {
      try {
        const runtimeConfig = useRuntimeConfig()
        const res = await $fetch(`${runtimeConfig.public.API_URL}/login`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Basic ${btoa(`${username}:${password}`)}`
          }
        })

        this.username = username
        this.password = password
        this.isLoggedIn = true

        console.info(res)
      } catch (error) {
        console.error('Login failed:', error)
        this.isLoggedIn = false
        throw new Error('Login failed. Please check your credentials.')
      }
    }
  }
})
