import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ClickerView from '@/views/ClickerView.vue'
import ChallengesView from '@/views/ChallengesView.vue'
import MyChallengesView from '@/views/MyChallengesView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HomeView,
    },
    {
      path: '/clicker',
      name: 'Clicker',
      component: ClickerView,
    },
    {
      path: '/challenges',
      name: 'Challenges',
      component: ChallengesView,
    },
    {
      path: '/my-challenges',
      name: 'MyChallenges',
      component: MyChallengesView,
    },
    {
      path: '/:catchAll(.*)*',
      component: () => import('@/views/404View.vue'),
    },
  ],
})

export default router
