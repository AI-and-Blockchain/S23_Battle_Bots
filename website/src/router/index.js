import Vue from 'vue'
import VueRouter from 'vue-router'
import KeyCheckpoint from '../views/KeyCheckpoint.vue'
import ViewBoard from '../views/ConnectFour.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'keyCheckpoint',
    props: true,
    component: KeyCheckpoint
  },
  {
    path: '/viewBoard',
    name: 'viewBoard',
    props: true,
    component: ViewBoard
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    // component: () => import(/* webpackChunkName: "about" */ '../views/ConnectFour.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
