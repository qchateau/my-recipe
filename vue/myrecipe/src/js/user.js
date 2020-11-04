import axios from 'axios'

export default {
  install (Vue) {
    Vue.prototype.$user = {
      data: Vue.observable({email: null, firstName: null, lastName: null, viewPermissions: []}),
      loggedIn () {
        return this.data.email !== null
      },
      async refresh () {
        try {
          let data = (await axios.get('backend/users/current')).data
          this.data.email = data.email
          this.data.firstName = data.first_name
          this.data.lastName = data.last_name
          this.data.viewPermissions = data.view_permissions

          console.log('Logged in:', this.data.email)
        } catch (exc) {
          this.data.email = null
          this.data.firstName = null
          this.data.lastName = null
          this.data.viewPermissions = []
          console.log('Not logged in', exc)
        }
      }
    }
  }
}
