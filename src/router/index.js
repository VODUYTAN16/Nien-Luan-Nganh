import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/views/HomeView.vue';
import PatternDetail from '@/views/PatternDetail.vue';
import ModelLab from '@/views/ModelLab.vue';
import AuthView from '@/views/AuthView.vue';
import PatternCatalog from '@/views/PatternCatalog.vue';
import SearchView from '@/views/SearchView.vue';

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/patterns', name: 'patterns', component: PatternCatalog },
  { path: '/patterns/:id', name: 'pattern-detail', component: PatternDetail },
  { path: '/models', name: 'models', component: ModelLab },
  { path: '/auth', name: 'auth', component: AuthView },
  { path: '/search', name: 'search', component: SearchView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
