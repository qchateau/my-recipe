<template>
  <v-app>
    <v-overlay :value="!$user.loggedIn()">
      <div style="text-align: center">
        <p>Please login with a Google account</p>
        <v-btn large @click="logInOut">{{ $user.loggedIn() ?"Logout" : "Login"}}</v-btn>
      </div>
    </v-overlay>

    <v-overlay :value="loading">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>

    <v-app-bar app>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <div style="cursor: pointer;" @click=" $router.push('/')">MyRecipe</div>

      <div style="text-align: right; width: 100%">
        <v-btn small text @click="logInOut">{{ $user.loggedIn() ?"Logout" : "Login"}}</v-btn>
      </div>
    </v-app-bar>

    <v-navigation-drawer app v-model="drawer" absolute temporary>
      <v-list nav dense>
        <v-list-item>
          <h3>Menu</h3>
        </v-list-item>

        <v-list-item @click="drawer = false; $router.push('/recipe-list')">
          <v-list-item-title>Recipes</v-list-item-title>
        </v-list-item>

        <v-list-item @click="drawer = false; $router.push('/new-recipe')">
          <v-list-item-title>New recipe</v-list-item-title>
        </v-list-item>

        <v-list-item @click="drawer = false; $router.push('/import-recipe')">
          <v-list-item-title>Import recipe</v-list-item-title>
        </v-list-item>

        <v-list-item>
          <h3>About</h3>
        </v-list-item>

        <v-list-item @click="openBugReport">
          <v-list-item-title>Report a bug</v-list-item-title>
        </v-list-item>

        <v-list-item @click="openGitHub">
          <v-list-item-title>GitHub</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main v-if="$user.loggedIn()">
      <v-container fluid id="main-container">
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
      loading: true,
      selected: 'recipe-list'
    }
  },
  async mounted () {
    await this.$user.refresh()
    this.loading = false
  },
  methods: {
    logIn () {
      this.loading = true
      location.href = '/backend/accounts/google/login/?next=' + location.href
    },
    async logOut () {
      this.loading = true
      await axios.post('/backend/accounts/logout/')
      this.$router.go()
    },
    async logInOut () {
      if (this.$user.loggedIn()) {
        await this.logOut()
      } else {
        this.logIn()
      }
    },
    openBugReport () {
      window.open('https://github.com/qchateau/my-recipe/issues/new', '_blank').focus()
    },
    openGitHub () {
      window.open('https://github.com/qchateau/my-recipe', '_blank').focus()
    }
  }
}
</script>

<style>
#main-container {
  max-width: 1000px;
}

header div {
  max-width: 1000px;
  margin-left: auto;
  margin-right: auto;
}

footer .row {
  max-width: 1000px;
  margin-left: auto;
  margin-right: auto;
}
</style>
