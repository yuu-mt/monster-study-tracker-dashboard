import { createRouter, createWebHistory } from 'vue-router'

// 要件定義書 3-1-b: 左タブ「進捗管理」はデフォルトで「受講中」フィルター表示
const routes = [
  {
    path: '/',
    redirect: '/trainees',
  },
  {
    path: '/trainees',
    name: 'TraineeList',
    component: () => import('../views/TraineeListView.vue'),
    meta: { title: '進捗管理' },
  },
  {
    path: '/trainees/:id',
    name: 'TraineeDetail',
    component: () => import('../views/TraineeDetailView.vue'),
    meta: { title: '進捗詳細' },
  },
  {
    path: '/trainees/register',
    name: 'TraineeRegister',
    component: () => import('../views/TraineeRegisterView.vue'),
    meta: { title: '受講生・メンバー登録' },
  },
  {
    path: '/curriculum',
    name: 'CurriculumManagement',
    component: () => import('../views/CurriculumManagementView.vue'),
    meta: { title: 'カリキュラム管理' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
