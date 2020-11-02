<template>
  <v-app>
    <v-app-bar app>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <div>MyRecipe</div>

      <div style="text-align: right; width: 100%">
        <v-btn small text @click="logInOut">{{ user ?"Logout" : "Login"}}</v-btn>
      </div>
    </v-app-bar>
    <v-navigation-drawer app v-model="drawer" absolute temporary>
      <v-list nav dense>
        <v-list-item @click="drawer = false; $router.push('/recipe-list')">
          <v-list-item-title>Recipes</v-list-item-title>
        </v-list-item>

        <v-list-item @click="drawer = false; $router.push('/new-recipe')">
          <v-list-item-title>New recipe</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-overlay :value="loading">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  data () {
    return {
      drawer: false,
      user: null,
      loading: true,
      selected: 'recipe-list'
    }
  },
  async mounted () {
    try {
      this.user = (await axios.get('backend/users/current')).data
      console.log('Logged in:', this.user.username)
    } catch (exc) {
      console.log('Not logged in')
    }
    this.loading = false
  },
  methods: {
    logIn () {
      this.loading = true
      location.href = '/backend/accounts/google/login/'
    },
    async logOut () {
      this.loading = true
      await axios.post('/backend/accounts/logout/')
      this.$router.go()
    },
    async logInOut () {
      if (this.user === null) {
        this.logIn()
      } else {
        await this.logOut()
      }
    }
  }
}
</script>

<style>
</style>
