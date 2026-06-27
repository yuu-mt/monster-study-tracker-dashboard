<template>
    <aside class="sidebar">
        <div class="sidebar-brand">
            <p class="brand-name">Monster Study Tracker</p>
            <p class="brand-name">カリキュラム管理</p>
        </div>

        <nav class="sidebar-nav">
            <p class="nav-section">メイン</p>
            <RouterLink to="/trainees" class="nav-item" >
                <i class="ti ti-users"></i>受講生一覧
            </RouterLink>
            <RouterLink to="/curriculum" class="nav-item">
                <i class="ti ti-book"></i>カリキュラム
            </RouterLink>

            <p class="nav-section mt">管理</p>
            <RouterLink to="/alerts" class="nav-item">
                <i class="ti ti-bell"></i>アラート
            </RouterLink>
            <RouterLink to="/settings" class="nav-item">
                <i class="ti ti-settings"></i>設定
            </RouterLink>
        </nav>

        <div class="sidebar-footer">
            <div class="user-row">
                <div class="avatar">{{ initials }}</div>
                <div class="user-info">
                    <p class="user-name">{{ authStore.user?.username }}</p>
                    <p class="user-role">インストラクター</p>
                </div>
                <button @click="logout" class="logout-btn" title="ログアウト">
                    <i class="ti ti-logout"></i>
                </button>
            </div>
        </div>
    </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const initials = computed(() => {
    const name = authStore.user?.username || ''
    return name.slice(0, 2)
})

async function logout() {
    authStore.logout()
    router.push('/login')
}
</script>

<style scoped>
.sidebar {
    width: 220px;
    flex-shrink: 0;
    background: white;
    border-right: 1px solid #e5e7eb;
    display: flex;
    flex-direction: column;
    height: 100vh;
}

.sidebar-brand {
    padding: 18px 16px 14px;
    border-bottom: 1px solid #e5e7eb;
}
.brand-name {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
}
.brand-sub {
    font-size: 11px;
    color: #9ca3af;
    margin-top: 2px;
}

.sidebar-nav {
    flex: 1;
    padding: 10px 8px;
    overflow-y: auto;
}
.nav-section {
    font-size: 10px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 8px 8px 4px;
}
.nav-section.mt {
    margin-top: 8px;
}
.nav-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 6px;
    font-size: 13px;
    color: #6b7280;
    text-decoration: none;
    margin-bottom: 2px;
    transition: background 0.15s, color 0.15s;
}
.nav-item i {
    font-size: 16px;
}
.nav-item:hover {
    background: #f3f4f6;
    color: #111827;
}
.nav-item.router-link-active {
    background: #ede9fe;
    color: #7c3aed;
}
.nav-item.router-link-active i {
    color: #7c3aed;
}

.sidebar-footer {
    padding: 12px 8px;
    border-top: 1px solid #e5e7eb;
}
.user-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 6px;
}
.avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #ede9fe;
    color: #7c3aed;
    font-size: 11px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.user-info {
    flex: 1;
    min-width: 0;
}
.user-name {
    font-size: 12px;
    font-weight: 500;
    color: #111827;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.user-role {
    font-size: 10px;
    color: #9ca3af;
}
.logout-btn {
    background: none;
    border: none;
    cursor: pointer;
    color: #9ca3af;
    padding: 4px;
    display: flex;
    align-items: center;
}
.logout-btn:hover {
    color: #374151;
}
.logout-btn i {
    font-size: 16px;
}
</style>