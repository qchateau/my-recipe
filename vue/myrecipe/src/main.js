// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import axios from 'axios'

import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

import VuetifyToast from 'vuetify-toast-snackbar'
import StayAwake from '@/js/stayawake.js'

import App from './App'
import router from './router'
import UserPlugin from '@/js/user.js'

StayAwake.init()

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

const vuetify = new Vuetify({theme: { dark: true }})

Vue.config.productionTip = false
Vue.use(Vuetify)
Vue.use(UserPlugin)

Vue.use(VuetifyToast, {
  $vuetify: vuetify.framework,
  x: 'center',
  y: 'top',
  color: 'info',
  icon: '',
  iconColor: '',
  classes: [
    'body-2'
  ],
  timeout: 3000,
  dismissable: true,
  multiLine: false,
  vertical: false,
  queueable: false,
  showClose: false,
  closeText: '',
  closeIcon: 'close',
  closeColor: '',
  slot: [],
  shorts: {},
  property: '$toast'
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  vuetify: vuetify,
  router,
  components: { App },
  template: '<App/>'
})
