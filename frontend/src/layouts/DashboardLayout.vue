<!-- src/layouts/DashboardLayout.vue -->
<template>
    <div class="dashboard-shell">
        <AppSidebar />
        <div class="main-area">
        <RouterView />
        </div>
    </div>
</template>

<script setup>
import AppSidebar from '@/components/AppSidebar.vue'
</script>

<style scoped>
.dashboard-shell {
    display: flex;
    height: 100vh;
    overflow: hidden;
}
.main-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: #f9fafb;
}
</style>