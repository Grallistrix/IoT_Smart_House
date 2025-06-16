import useUserStore from '~/store/user.store'

export default defineNuxtRouteMiddleware((to) => {
  const userStore = useUserStore()

  if (to.fullPath === '/login') {
    // If the user is already logged in, redirect them to the home page
    if (userStore.isLoggedIn) {
      return navigateTo('/')
    }
  } else if (!userStore.isLoggedIn) {
    // If the user is not logged in and trying to access a protected route,
    // redirect them to the login page
    return navigateTo('/login')
  }
})
