import NoSleep from 'nosleep.js'

const noSleep = new NoSleep()

export default {
  install (Vue) {
    Vue.prototype.$nosleep = {
      data: Vue.observable({enabled: false}),
      isEnabled () {
        return this.data.enabled
      },
      enable () {
        noSleep.enable()
        this.data.enabled = true
      },
      disable () {
        this.data.enabled = false
        noSleep.disable()
      },
      toggle () {
        if (this.data.enabled) {
          this.disable()
        } else {
          this.enable()
        }
      }
    }
  }
}
