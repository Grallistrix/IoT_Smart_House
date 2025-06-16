<script setup lang="ts">
const $runtime = useRuntimeConfig()

useHead({
  title: $runtime.public.APP_TITLE
})
</script>

<template>
  <div class="flex flex-col flex-1 index-page">
    <h1>Welcome to IoT Panel</h1>
  </div>
</template>
