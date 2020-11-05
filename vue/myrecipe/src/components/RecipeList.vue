<template>
  <div>
    <v-overlay :value="loading">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>

    <v-text-field hide-details label="Search" v-model="nameSearch"></v-text-field>

    <v-list dense>
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

    <v-footer fixed>
      <div style="margin: auto">
        <v-pagination v-model="currentPage" :length="Math.floor((recipeCount - 1) / pageSize) + 1"></v-pagination>
      </div>
    </v-footer>
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
      pageSize: 1,
      recipeCount: 0,
      recipeList: [],
      loading: false
    }
  },
  async mounted () {
    await this.loadPage(1)
  },
  methods: {
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
    async loadPage (page) {
      this.loading = true
      try {
        let params = {
          page: page
        }
        if (this.nameSearch.trim() !== '') {
          params['name-search'] = this.nameSearch.trim()
        }
        let res = (await axios.get('/backend/recipes/', {params: params})).data
        this.recipeCount = res.count
        this.pageSize = Math.max(this.pageSize, res.results.length)
        this.recipeList = res.results
      } catch (exc) {
        console.error(exc)
      }
      this.loading = false
    }
  },
  watch: {
    async nameSearch () {
      await this.loadPage(this.currentPage)
    },
    async currentPage () {
      await this.loadPage(this.currentPage)
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
