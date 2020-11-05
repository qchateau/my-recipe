<template>
  <div>
    <v-overlay :value="loading">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>

    <h3>Import recipe</h3>

    <v-form ref="form" v-model="valid">
      <v-text-field v-model="importUrl" :rules="importUrlRules" label="URL" required></v-text-field>

      <v-btn :disabled="!valid" color="success" @click="doImportUrl" block>
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
        v => !!v.match(localRecipeUrlRegex) || 'URL not supported'
      ]
    }
  },
  methods: {
    async doImportUrl () {
      this.loading = true
      try {
        if (this.importUrl.match(localRecipeUrlRegex)) {
          await this.importLocalRecipe(this.importUrl)
        }
      } catch (exc) {
        console.error(exc)
        this.$toast.error('Failed to import recipe.')
      }
      this.$toast.success('Recipe imported.')
      this.loading = false
    },
    async importLocalRecipe (url) {
      let id = url.match(localRecipeUrlRegex)[1]
      let data = (await axios.get('/backend/recipes/' + id + '/')).data

      const formData = new FormData()
      for (const [key, value] of Object.entries(data)) {
        if (key === 'image' && value !== null) {
          let imageBlob = new Blob([(await axios.get(value, {responseType: 'blob'})).data])
          formData.append(key, imageBlob, tools.uuid4() + '.png')
        } else {
          formData.append(key, value)
        }
      }

      await axios.post('/backend/recipes/', formData)
      this.$router.push('/edit-recipe/' + id)
    }
  }
}
</script>

<style scoped>
</style>
