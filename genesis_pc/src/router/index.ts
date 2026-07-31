import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import { getToken } from '@/utils/storage'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/common/LoginPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/select-store',
    name: 'StoreSelect',
    component: () => import('@/views/common/StoreSelectPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardPage.vue'),
        meta: { title: '工作台', icon: 'Odometer' },
      },
      {
        path: '/vip',
        name: 'VipList',
        component: () => import('@/views/vip/VipListPage.vue'),
        meta: { title: '会员管理', icon: 'User' },
      },
      {
        path: '/vip/:id',
        name: 'VipDetail',
        component: () => import('@/views/vip/VipDetailPage.vue'),
        meta: { title: '会员详情', hidden: true },
      },
      {
        path: 'adviser/billing',
        name: 'Billing',
        component: () => import('@/views/adviser/BillingPage.vue'),
        meta: { title: '手工开单', icon: 'Ticket' },
      },
      {
        path: 'adviser/billing-v2',
        name: 'BillingV2',
        component: () => import('@/views/adviser/BillingPageV2.vue'),
        meta: { title: '手工开单', icon: 'Ticket' },
      },
      {
        path: 'adviser/hungs',
        name: 'HungOrders',
        component: () => import('@/views/adviser/HungOrdersPage.vue'),
        meta: { title: '挂单管理', icon: 'List' },
      },
      {
        path: '/cashier/checkout',
        name: 'CashierCheckout',
        component: () => import('@/views/cashier/CheckoutPage.vue'),
        meta: { title: '收银结账', icon: 'Coin' },
      },
      {
        path: '/cashier/modify',
        name: 'CashierModify',
        component: () => import('@/views/cashier/ModifyPage.vue'),
        meta: { title: '修改单据', icon: 'Edit' },
      },
      {
        path: '/cashier/void',
        name: 'CashierVoid',
        component: () => import('@/views/cashier/VoidPage.vue'),
        meta: { title: '作废单据', icon: 'Delete' },
      },
      {
        path: '/cashier/shift',
        name: 'CashierShift',
        component: () => import('@/views/cashier/ShiftPage.vue'),
        meta: { title: '交班日结', icon: 'Transfer' },
      },

      {
        path: '/booking',
        name: 'Booking',
        component: () => import('@/views/booking/BookingPage.vue'),
        meta: { title: '预约管理', icon: 'Calendar' },
      },
      {
        path: '/goods',
        name: 'Goods',
        component: () => import('@/views/goods/GoodsPage.vue'),
        meta: { title: '商品管理', icon: 'Goods' },
      },
      {
        path: "/goods/stock",
        name: "GoodsStock",
        component: () => import("@/views/goods/StockPage.vue"),
        meta: { title: "进出货管理", icon: "Box" },
      },
      {
        path: '/report',
        name: 'Report',
        component: () => import('@/views/report/ReportPage.vue'),
        meta: { title: '卡余额汇总', icon: 'DataAnalysis' },
      },
      {
        path: 'report/performance',
        name: 'StorePerformance',
        component: () => import('@/views/report/StorePerformancePage.vue'),
        meta: { title: '门店业绩', icon: 'DataAnalysis' },
      },
      {
        path: '/crm',
        name: 'Crm',
        component: () => import('@/views/crm/CrmPage.vue'),
        meta: { title: '客户关怀', icon: 'ChatDotSquare' },
      },
      {
        path: '/campaign',
        name: 'Campaign',
        component: () => import('@/views/campaign/CampaignPage.vue'),
        meta: { title: '营销活动', icon: 'Promotion' },
      },
      {
        path: '/assistant',
        name: 'Assistant',
        component: () => import('@/views/assistant/AssistantPage.vue'),
        meta: { title: 'AI 助手', icon: 'MagicStick' },
      },
      {
        path: '/datamanage',
        name: 'DataManage',
        component: () => import('@/views/datamanage/DataManagePage.vue'),
        meta: { title: '数据管理', icon: 'Setting' },
      },
      {
        path: '/sysadmin/serviece',
        name: 'ServieceAdmin',
        component: () => import('@/views/sysadmin/ServieceAdminPage.vue'),
        meta: { title: '服务管理' },
      },
      {
        path: '/sysadmin/goods',
        name: 'GoodsAdmin',
        component: () => import('@/views/sysadmin/GoodsAdminPage.vue'),
        meta: { title: '商品管理' },
      },
      {
        path: '/sysadmin/cardtype',
        name: 'CardtypeAdmin',
        component: () => import('@/views/sysadmin/CardtypeAdminPage.vue'),
        meta: { title: '卡类管理' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = getToken()
  const company = localStorage.getItem('genesis_pc_company')
  const storecode = localStorage.getItem('genesis_pc_storecode')

  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else if (to.path === '/login' && token && company) {
    next('/')
  } else if (to.path === '/select-store') {
    next()
  } else if (to.path !== '/login' && to.path !== '/select-store' && token && company && !storecode) {
    next('/select-store')
  } else {
    next()
  }
})

export default router
