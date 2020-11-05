<template>
  <div>
    <v-overlay :value="!data">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>

    <div v-if="data">
      <h3>{{ edit ? "Editing recipe" : "New recipe"}}</h3>

      <v-form ref="form" v-model="valid">
        <v-text-field v-model="data.name" :counter="250" :rules="nameRules" label="Name" required></v-text-field>

        <v-textarea rows="1" auto-grow v-model="data.description" label="Description"></v-textarea>

        <v-checkbox v-model="data.public" label="Public (people with link can view)"></v-checkbox>

        <h4>Ingredients</h4>

        <v-card
          style="margin: 5px 0px"
          v-for="ingredient in data.ingredients"
          :key="ingredient.key"
        >
          <v-card-text>
            <v-row dense>
              <v-col cols="6" md="2">
                <v-text-field
                  dense
                  v-model="ingredient.quantity"
                  hide-details
                  single-line
                  type="number"
                />
              </v-col>
              <v-col cols="6" md="3">
                <v-text-field dense v-model="ingredient.unit" hide-details single-line />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  dense
                  v-model="ingredient.name"
                  hide-details
                  single-line
                  @input="ingredientNamedChanged(ingredient)"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <v-btn :disabled="!valid" color="success" @click="createOrUpdate" block>
          <v-icon>mdi-check</v-icon>
        </v-btn>
      </v-form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

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
      valid: true,
      nameRules: [
        v => !!v || 'Name is required',
        v => (v && v.length >= 10) || 'Name must be at least than 10 characters',
        v => (v && v.length <= 250) || 'Name must be less than 250 characters'
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
        ingredients: []
      }
    }

    if (this.data.ingredients.length === 0) {
      this.addIngredient()
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
      this.busy = false
    },
    async create () {
      try {
        let data = (await axios.post('/backend/recipes/', this.generatePostData())).data
        this.$toast.success('Recipe created.')
        this.$router.push('/edit-recipe/' + data.id + '/')
      } catch (exc) {
        console.error(exc)
        this.$toast.error('Failed to create the recipe.')
      }
    },
    async update () {
      try {
        await axios.put('/backend/recipes/' + this.data.id + '/', this.generatePostData())
        this.$toast.success('Recipe updated.')
      } catch (exc) {
        console.error(exc)
        this.$toast.error('Failed to update the recipe.')
      }
    },
    ingredientNamedChanged (ingredient) {
      if (ingredient.key !== this.data.ingredients[this.data.ingredients.length - 1].key) {
        return
      }
      if (ingredient.name !== '') {
        this.addIngredient()
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
      let data = {
        name: this.data.name,
        description: this.data.description,
        public: this.data.public,
        ingredients: []
      }

      for (let ingredient of this.data.ingredients) {
        if (ingredient.name === '') {
          continue
        }
        data.ingredients.push(ingredient)
      }
      return data
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
</style>
