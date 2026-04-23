import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ChallengesView from '@/views/ChallengesView.vue'
import MyChallengesView from '@/views/MyChallengesView.vue'
import ChallengeDetailView from '@/views/ChallengeDetailView.vue'
import MGlyphDetailView from '@/views/MGlyphDetailView.vue'
import CreateChallengeView from '@/views/CreateChallengeView.vue'
import MyInvitesView from '@/views/MyInvitesView.vue'
import AdminInvitesView from '@/views/AdminInvitesView.vue'
import ChallengeEvaluationView from '@/views/ChallengeEvaluationView.vue'
import SelfEvaluationView from '@/views/SelfEvaluationView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HomeView,
    },
    {
      path: '/challenges',
      name: 'Challenges',
      component: ChallengesView,
    },
    {
      path: '/challenge/:id',
      name: 'ChallengeDetail',
      component: ChallengeDetailView,
    },
    {
      path: '/challenge/:id/evaluation',
      name: 'ChallengeEvaluation',
      component: ChallengeEvaluationView,
    },
    {
      path: '/my-challenges',
      name: 'MyChallenges',
      component: MyChallengesView,
    },
    {
      path: '/mglyph/:id',
      name: 'MGlyphDetail',
      component: MGlyphDetailView,
    },
    {
      path: '/create-challenge',
      name: 'CreateChallenge',
      component: CreateChallengeView,
    },
    {
      path: '/my-invites',
      name: 'MyInvites',
      component: MyInvitesView,
    },
    {
      path: '/admin-invites',
      name: 'AdminInvites',
      component: AdminInvitesView,
    },
    {
      path: '/evaluation',
      name: 'SelfEvaluation',
      component: SelfEvaluationView,
    },
    {
      path: '/:catchAll(.*)*',
      component: () => import('@/views/404View.vue'),
    },
  ],
})

export default router
