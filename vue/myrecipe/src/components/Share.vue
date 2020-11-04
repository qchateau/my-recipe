<template>
  <div>
    <v-overlay :value="loading">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>

    <h3>Share</h3>

    <div>You are sharing your recipe with {{ viewPermissionsEmails.length }} people.</div>

    <div style="min-height: 50px"></div>

    <v-form ref="addForm" v-model="addFormValid">
      <v-text-field v-model="addEmail" :rules="addEmailRules" label="E-mail" required type="email"></v-text-field>

      <v-btn :disabled="!addValid" color="success" @click="onAdd" block>
        <v-icon>mdi-check</v-icon>Add
      </v-btn>
    </v-form>

    <div style="min-height: 50px"></div>

    <v-form ref="deleteForm">
      <v-autocomplete v-model="deleteEmail" :items="viewPermissionsEmails" label="E-mail"></v-autocomplete>

      <v-btn :disabled="!deleteValid" color="error" @click="onDelete" block>
        <v-icon>mdi-delete</v-icon>Remove
      </v-btn>
    </v-form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Share',
  data () {
    return {
      loading: true,
      addFormValid: false,
      viewPermissionsEmails: [],
      addEmail: '',
      deleteEmail: '',
      addEmailRules: [
        v => !!v || 'E-mail is required',
        v => /.+@.+/.test(v) || 'E-mail must be valid',
        v => v !== this.$user.data.email || 'E-mail cannot be yours'
      ]
    }
  },
  async mounted () {
    await this.update()
    this.loading = false
  },
  methods: {
    async update () {
      await this.$user.refresh()
      this.viewPermissionsEmails = this.$user.data.viewPermissions
      if (this.viewPermissionsEmails.length > 0) {
        this.deleteEmail = this.viewPermissionsEmails[0]
      }
    },
    async onAdd () {
      this.loading = true
      try {
        await axios.post('/backend/users/give-permission/', {email: this.addEmail})
        this.$toast.success('Recipes are now shared with ' + this.addEmail)
      } catch (exc) {
        console.error(exc)
        this.$toast.error('Failed to share recipes with ' + this.addEmail)
      }
      await this.update()
      this.loading = false
    },
    async onDelete () {
      this.loading = true
      try {
        await axios.post('/backend/users/revoke-permission/', {email: this.deleteEmail})
        this.$toast.success('Recipes no longer shared with ' + this.deleteEmail)
      } catch (exc) {
        console.error(exc)
        this.$toast.error('Failed to delete sharing with ' + this.deleteEmail)
      }
      await this.update()
      this.loading = false
    }
  },
  computed: {
    addValid () {
      return this.addFormValid && this.$user.loggedIn()
    },
    deleteValid () {
      return !!this.deleteEmail && this.$user.loggedIn()
    }
  }
}
</script>

<style scoped>
</style>
