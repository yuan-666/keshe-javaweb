import { createRouter, createWebHistory } from 'vue-router';
import AdminLogin from './components/AdminLogin.vue';
import ClassList from './components/ClassList.vue';
import TicketStats from './components/TicketStats.vue';
import TicketPurchase from './components/TicketPurchase.vue';
import TicketRefund from './components/TicketRefund.vue';
import UserLogin from './components/UserLogin.vue';
import UserRegister from './components/UserRegister.vue';
import ExportTickets from './components/ExportTickets.vue';

const routes = [
  { path: '/', redirect: '/user-login' },
  { path: '/login', component: AdminLogin },
  { path: '/user-login', component: UserLogin },
  { path: '/user-register', component: UserRegister },
  // 管理员专属页面
  { path: '/classes', component: ClassList, meta: { requiresAdmin: true } },
  { path: '/stats', component: TicketStats, meta: { requiresAdmin: true } },
  { path: '/import-export', component: ExportTickets, meta: { requiresAdmin: true } },
  // 用户专属页面
  { path: '/user-purchase', component: TicketPurchase, meta: { requiresUser: true } },
  { path: '/user-refund', component: TicketRefund, meta: { requiresUser: true } },
  // 管理员也可访问购票/退票（如需）
  { path: '/purchase', component: TicketPurchase, meta: { requiresAdmin: true } },
  { path: '/refund', component: TicketRefund, meta: { requiresAdmin: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAdmin = localStorage.getItem('admin') === '1';
  const isUser = localStorage.getItem('user') === '1';
  if (to.meta.requiresAdmin && !isAdmin) {
    next('/login');
  } else if (to.meta.requiresUser && !isUser) {
    next('/user-login');
  } else if (to.path === '/login' && isAdmin) {
    next('/classes');
  } else if (to.path === '/user-login' && isUser) {
    next('/user-purchase');
  } else {
    next();
  }
});

export default router;
