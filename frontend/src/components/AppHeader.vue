<template>
    <header class="app-header">
        <h1 class="page-title">{{ title }}</h1>
        <slot />
    </header>
</template>

<script setup>
defineProps({
    title: {
        type: String,
        default: ''
    }
})
</script>

<style scoped>
.app-header {
    height: 52px;
    background: white;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    align-items: center;
    padding: 0 24px;
    gap: 12px;
    flex-shrink: 0;
}
.page-title {
    font-size: 15px;
    font-weight: 600;
    color: #111827;
    flex: 1;
}
</style>