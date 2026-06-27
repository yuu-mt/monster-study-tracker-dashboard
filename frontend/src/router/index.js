import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import LoginPage from '../pages/LoginPage.vue'

const routes = [
  {
    path: '/login',
    component: LoginPage
  },
  {
    path: '/',
    component: DashboardLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/trainees'
      },
      {
        path: 'trainees',
        component: () => import('@/pages/TraineesPage.vue')
      },
      {
        path: 'trainees/:id',
        component: () => import('@/pages/TraineeDetailPage.vue')
      },
      {
        path: 'curriculum',
        component: () => import('@/pages/CurriculumPage.vue')
      },
      {
        path: 'alerts',
        component: () => import('@/pages/AlertsPage.vue')
      },
      {
        path: 'settings',
        component: () => import('@/pages/SettingsPage.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/trainees'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return '/login'
  }
})

export default router