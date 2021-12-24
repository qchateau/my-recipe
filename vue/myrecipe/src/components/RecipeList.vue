<template>
  <div>
    <v-overlay :value="loading">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>

    <v-text-field hide-details label="Search" v-model="nameSearch" autocomplete="off"></v-text-field>

    <v-list dense v-if="filteredRecipeList.length > 0">
      <v-list-item
        v-for="recipe in filteredRecipeList"
        :key="'item'+recipe.id"
        @click="$router.push('recipe/' + recipe.id)"
      >
        <v-list-item-content>
          <v-list-item-title>{{ recipe.name }}</v-list-item-title>
          <v-list-item-subtitle>{{ recipe.author.first_name }} {{ recipe.author.last_name }}</v-list-item-subtitle>
        </v-list-item-content>

        <v-list-item-avatar v-if="recipe.image">
          <img :src="recipe.image" />
        </v-list-item-avatar>
      </v-list-item>
    </v-list>

    <div style="text-align: center; padding-top: 50px" v-else>
      <div style>No recipes</div>
    </div>

    <v-speed-dial v-model="fab" bottom right fixed>
      <template v-slot:activator>
        <v-btn v-model="fab" color="blue darken-2" fab>
          <v-icon v-if="fab">mdi-close</v-icon>
          <v-icon v-else>mdi-plus</v-icon>
        </v-btn>
      </template>

      <v-btn fab small color="green" @click="$router.push('/new-recipe/')">
        <v-icon>mdi-playlist-plus</v-icon>
      </v-btn>

      <v-btn fab small color="green" @click="$router.push('/import-recipe/')">
        <v-icon>mdi-import</v-icon>
      </v-btn>
    </v-speed-dial>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RecipeList',
  data () {
    return {
      nameSearch: '',
      currentPage: 1,
      recipeList: [],
      loading: false,
      fab: false,
      bottom: false
    }
  },
  async mounted () {
    const refreshBottomStatus = () => {
      this.bottom = this.bottomVisible()
    }
    window.addEventListener('scroll', refreshBottomStatus)
    this.refreshBottomInterval = setInterval(refreshBottomStatus, 500)
    refreshBottomStatus()

    await this.loadNext()
  },
  unmounted () {
    clearInterval(this.refreshBottomInterval)
  },
  methods: {
    bottomVisible () {
      return Math.max(window.pageYOffset, document.documentElement.scrollTop, document.body.scrollTop) + window.innerHeight === document.documentElement.offsetHeight
    },
    formatterDate (row, col, value) {
      const options = {dateStyle: 'medium'}
      return (new Date(value)).toLocaleDateString(navigator.language, options)
    },
    formatterAuthor (row, col, value) {
      return value.first_name + ' ' + value.last_name
    },
    onRowClick (row) {
      this.$router.push('recipe/' + row.id)
    },
    async loadOnePage (page) {
      this.loading = true
      let res = null
      try {
        let params = {
          page: page
        }
        if (this.nameSearch.trim() !== '') {
          params['name-search'] = this.nameSearch.trim()
        }
        res = (await axios.get('/backend/recipes/', {
          params: params,
          validateStatus: (status) => status === 200 || status === 404
        })).data.results
      } catch (exc) {
        console.error(exc)
      }
      this.loading = false
      return res || []
    },
    async loadNext () {
      const next = await this.loadOnePage(this.currentPage++)
      for (let recipe of next) {
        this.recipeList.push(recipe)
      }
    },
    async resetRecipeList () {
      this.currentPage = 1
      this.recipeList = []
      await this.loadNext()
    }
  },
  watch: {
    async nameSearch () {
      await this.resetRecipeList()
    },
    async bottom () {
      if (this.bottom) {
        await this.loadNext()
      }
    }
  },
  computed: {
    filteredRecipeList () {
      if (!this.nameSearch) {
        return this.recipeList
      }

      return this.recipeList.filter(data => data.name.toLowerCase().includes(this.nameSearch.toLowerCase()))
    }
  }
}
</script>

<style scoped>
</style>
