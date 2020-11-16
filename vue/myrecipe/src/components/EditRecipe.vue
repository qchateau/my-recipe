<template>
  <div>
    <v-overlay :value="!data">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>

    <div v-if="data" class="main">
      <h3>{{ edit ? "Editing recipe" : "New recipe"}}</h3>

      <v-form ref="form" v-model="valid" autocomplete="off">
        <v-text-field v-model="data.name" :counter="250" :rules="nameRules" label="Name" required></v-text-field>

        <v-textarea
          rows="1"
          auto-grow
          v-model="data.description"
          :rules="descriptionRules"
          label="Description"
          required
        ></v-textarea>

        <v-file-input
          v-model="image"
          accept="image/*"
          prepend-icon="mdi-image"
          label="Picture (5MB max)"
        ></v-file-input>

        <v-checkbox v-model="data.public" label="Public (people with link can view)"></v-checkbox>

        <h4>Ingredients</h4>

        <v-card
          style="margin: 5px 0px"
          v-for="ingredient in data.ingredients"
          :key="ingredient.key"
        >
          <v-card-text>
            <v-row dense>
              <v-col cols="4" md="2">
                <v-text-field
                  dense
                  v-model="ingredient.quantity"
                  hide-details
                  single-line
                  type="number"
                  label="Quantity"
                />
              </v-col>
              <v-col cols="6" md="3">
                <v-text-field
                  dense
                  v-model="ingredient.unit"
                  hide-details
                  single-line
                  label="Unit"
                />
              </v-col>

              <v-col cols="2" md="1" v-if="!$vuetify.breakpoint.mdAndUp">
                <v-btn small @click="removeIngredient(ingredient)" color="error darken-1">
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  dense
                  v-model="ingredient.name"
                  hide-details
                  single-line
                  label="Ingredient"
                />
              </v-col>

              <v-col cols="2" md="1" v-if="$vuetify.breakpoint.mdAndUp">
                <v-btn small @click="removeIngredient(ingredient)" color="error darken-1" block>
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <v-btn @click="addIngredient()" color="grey darken-2" block>
          <v-icon>mdi-plus</v-icon>
        </v-btn>
      </v-form>
    </div>

    <v-footer fixed class="footer">
      <v-row>
        <v-col :cols="6" class="no-v-padding">
          <v-btn @click="close" color="grey darken-3" block>
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-col>
        <v-col :cols="6" class="no-v-padding">
          <v-btn :disabled="!valid" color="success" @click="createOrUpdate" block>
            <v-icon>mdi-check</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </v-footer>
  </div>
</template>

<script>
import axios from 'axios'
import tools from '@/js/tools.js'

export default {
  name: 'EditRecipe',
  props: {
    editId: {
      default: false
    }
  },
  data () {
    return {
      data: null,
      image: null,
      valid: true,
      nameRules: [
        v => !!v || 'Name is required',
        v => (v && v.length <= 250) || 'Name must be less than 250 characters'
      ],
      descriptionRules: [
        v => !!v || 'Description is required'
      ],
      busy: false,
      counter: 0
    }
  },
  async mounted () {
    if (this.edit) {
      try {
        this.data = (await axios.get('/backend/recipes/' + this.editId + '/')).data
      } catch (exc) {
        this.$toast.error('Failed to get the recipe.')
        this.$router.push('/')
      }
      for (let ingredient of this.data.ingredients) {
        ingredient.key = this.counter++
      }
    } else {
      this.data = {
        name: '',
        description: '',
        public: true,
        ingredients: []
      }
    }
  },
  methods: {
    async createOrUpdate () {
      this.busy = true
      if (this.edit) {
        await this.update()
      } else {
        await this.create()
      }
      this.goToRecipe()
      this.busy = false
    },
    async create () {
      try {
        let data = (await axios.post('/backend/recipes/', this.generatePostData())).data
        await this.uploadImage()

        this.$toast.success('Recipe created.')
        this.$router.push('/edit-recipe/' + data.id + '/')
      } catch (exc) {
        console.error(exc)
        this.$toast.error('Failed to create the recipe.')
      }
    },
    async update () {
      try {
        await Promise.all([
          axios.patch('/backend/recipes/' + this.data.id + '/', this.generatePostData()),
          this.uploadImage()
        ])

        this.$toast.success('Recipe updated.')
      } catch (exc) {
        console.error(exc)
        this.$toast.error('Failed to update the recipe.')
      }
    },
    addIngredient () {
      let key = this.counter++
      this.data.ingredients.push({
        key: key,
        quantity: 0,
        unit: '',
        name: ''
      })
    },
    removeIngredient (ingredient) {
      if (this.data.ingredients.length === 0) {
        return
      }
      this.data.ingredients = this.data.ingredients.filter(i => i.key !== ingredient.key)
    },
    generatePostData () {
      let ingredients = []

      for (let ingredient of this.data.ingredients) {
        if (ingredient.name === '') {
          continue
        }
        ingredients.push(ingredient)
      }

      return {
        name: this.data.name,
        description: this.data.description,
        public: this.data.public,
        ingredients: ingredients
      }
    },
    async uploadImage () {
      if (!this.image) {
        return
      }
      const data = new FormData()
      data.append('image', this.image, tools.uuid4() + '.png')
      await axios.patch('/backend/recipes/' + this.data.id + '/', data)
    },
    goToRecipe () {
      this.$router.push('/recipe/' + this.editId)
    },
    close () {
      if (this.editId) {
        this.goToRecipe()
      } else {
        this.$router.push('/recipe-list')
      }
    }
  },
  computed: {
    edit () {
      return this.editId !== false
    }
  }
}
</script>

<style scoped>
.main {
  padding-bottom: 100px;
}

.no-v-padding {
  padding-top: 0px;
  padding-bottom: 0px;
}
</style>
