<template>
  <div>
    <v-overlay :value="loading">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>

    <h3>Import recipe</h3>
    <p class="subtitle-2 text--secondary">
      Paste a MyRecipe link or any recipe webpage URL to extract and create a recipe.
    </p>

    <v-form ref="form" autocomplete="off" v-model="valid">
      <v-text-field
        v-model="importUrl"
        :rules="importUrlRules"
        label="URL"
        placeholder="https://..."
        hint="Supports MyRecipe links and external cooking recipe web pages"
        persistent-hint
        required
      ></v-text-field>

      <v-btn :disabled="!valid" color="success" @click="doImportUrl" block class="mt-4">
        <v-icon>mdi-check</v-icon>
      </v-btn>
    </v-form>
  </div>
</template>

<script>
import axios from 'axios'
import tools from '@/js/tools.js'

const localRecipeUrlRegexPattern = window.location.origin.replaceAll('/', '\\/').replaceAll('.', '\\.') + '.*\\/recipe\\/(.*)(\\/.*)?'
const localRecipeUrlRegex = new RegExp(localRecipeUrlRegexPattern)

export default {
  name: 'ImportRecipe',
  data () {
    return {
      loading: false,
      valid: false,
      importUrl: '',
      importUrlRules: [
        v => !!v || 'URL is required',
        v => /^https?:\/\/.+/i.test(v) || 'Must be a valid HTTP or HTTPS URL'
      ]
    }
  },
  methods: {
    async doImportUrl () {
      this.loading = true
      try {
        if (localRecipeUrlRegex.test(this.importUrl)) {
          await this.importLocalRecipe(this.importUrl)
          this.$toast.success('Recipe imported.')
        } else {
          let res = await axios.post('/backend/recipes/extract-url/', { url: this.importUrl })
          sessionStorage.setItem('prefillRecipe', JSON.stringify(res.data))
          this.$toast.success('Recipe extracted! Please review and save.')
          this.$router.push('/new-recipe')
        }
      } catch (exc) {
        console.error(exc)
        let errorMsg = exc.response && exc.response.data && exc.response.data.detail
          ? exc.response.data.detail
          : 'Failed to import recipe.'
        this.$toast.error(errorMsg)
      } finally {
        this.loading = false
      }
    },
    async importLocalRecipe (url) {
      let id = url.match(localRecipeUrlRegex)[1]
      let data = await tools.importId(id)
      this.$router.push('/recipe/' + data.id)
    }
  }
}
</script>

<style scoped>
</style>
