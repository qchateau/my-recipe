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

      let imageFormData = null
      if (data.image !== undefined) {
        imageFormData = new FormData()
        let imageBlob = new Blob([(await axios.get(data.image, {responseType: 'blob'})).data])
        imageFormData.append('image', imageBlob, tools.uuid4() + '.png')
        delete data.image
      }

      data = (await axios.post('/backend/recipes/', data)).data
      if (imageFormData) {
        await axios.patch(data.url, imageFormData)
      }
      this.$router.push('/edit-recipe/' + id)
    }
  }
}
</script>

<style scoped>
</style>
