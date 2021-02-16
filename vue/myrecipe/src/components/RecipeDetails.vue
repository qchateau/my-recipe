<template>
  <div>
    <v-overlay :value="!data">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>

    <div v-if="data">
      <div style="text-align: center">
        <h3>{{data.name}}</h3>
        <i style="font-size: 80%">{{data.author.first_name}} {{data.author.last_name}}</i>
      </div>

      <v-card-text>
        <div style="text-align: center">
          <img :src="data.image" width="256" style="border-radius: 5%" v-if="data.image" />
        </div>

        <v-card id="ingredients-card" v-if="data.ingredients.length > 0">
          <div style="float: right; margin: 5px"></div>
          <ul>
            <li
              v-for="ingredient in data.ingredients"
              :key="ingredient.id"
            >{{ ingredientQuantity(ingredient) }} {{ ingredient.unit }} {{ ingredient.name }}</li>
          </ul>
        </v-card>

        <pre id="description">{{ data.description }}</pre>
        <div style="min-height: 50px" />
      </v-card-text>

      <v-speed-dial v-model="fab" bottom right fixed>
        <template v-slot:activator>
          <v-btn v-model="fab" color="blue darken-2" fab>
            <v-icon v-if="fab">mdi-close</v-icon>
            <v-icon v-else>mdi-plus</v-icon>
          </v-btn>
        </template>

        <v-btn fab small color="indigo" @click="scaleDrawer = !scaleDrawer">
          <v-icon>mdi-scale</v-icon>
        </v-btn>

        <v-btn fab small color="blue" @click="onShare" v-if="data.public">
          <v-icon>mdi-content-copy</v-icon>
        </v-btn>

        <v-btn fab small color="blue" @click="importDialog = true" v-if="data.public && !owner">
          <v-icon>mdi-download</v-icon>
        </v-btn>

        <v-btn fab small color="green" @click="$router.push('/edit-recipe/'+id+'/')" v-if="owner">
          <v-icon>mdi-playlist-edit</v-icon>
        </v-btn>

        <v-btn fab small color="red" @click="deleteDialog = true" v-if="owner">
          <v-icon>mdi-delete</v-icon>
        </v-btn>
      </v-speed-dial>
    </div>

    <v-navigation-drawer v-model="scaleDrawer" fixed temporary bottom>
      <div style="padding: 20px 10px 10px 10px">
        <span>
          <v-text-field
            dense
            label="Scale"
            type="number"
            v-bind:value="Math.round(quantityScale*1000) / 1000"
            v-on:input="quantityScale = $event"
          />
        </span>
        <span v-if="data">
          <v-text-field
            dense
            type="number"
            :label="ingredient.name"
            :suffix="ingredient.unit"
            :key="ingredient.id"
            v-for="ingredient in data.ingredients"
            v-bind:value="ingredientQuantity(ingredient)"
            v-on:input="quantityScale = $event / ingredient.quantity"
          ></v-text-field>
        </span>
      </div>
    </v-navigation-drawer>

    <v-dialog v-model="importDialog" max-width="290">
      <v-card>
        <v-card-title class="headline">Import recipe</v-card-title>
        <v-card-text>This will make a copy of this recipe in your own library.</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="importDialog = false">Cancel</v-btn>
          <v-btn color="green darken-1" text @click="doImport(); importDialog = false">Import</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="deleteDialog" max-width="290">
      <v-card>
        <v-card-title class="headline">Delete recipe</v-card-title>
        <v-card-text>This will permanently delete the recipe.</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="deleteDialog = false">Cancel</v-btn>
          <v-btn color="red darken-1" text @click="doDelete(); deleteDialog = false">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import tools from '@/js/tools.js'

export default {
  name: 'RecipeDetails',
  props: ['id'],
  data () {
    return {
      data: null,
      quantityScale: 1,
      scaleDrawer: false,
      fab: false,
      deleteDialog: false,
      importDialog: false
    }
  },
  async mounted () {
    try {
      this.data = (await axios.get('/backend/recipes/' + this.id + '/')).data
      document.title = 'MyRecipe - ' + this.data.name
    } catch (exc) {
      console.error(exc)
      this.$toast.error('Failed to get recipe.')
      this.$router.push('/')
    }
  },
  methods: {
    async doDelete () {
      try {
        await axios.delete('/backend/recipes/' + this.id + '/')
        this.$toast.success('Recipe deleted.')
        this.$router.push('/')
      } catch (exc) {
        this.$toast.error('Failed to delete recipe.')
      }
    },
    async onShare () {
      await navigator.clipboard.writeText(location.href)
      this.$toast.success('Recipe URL copied to clipboard')
    },
    async doImport () {
      try {
        let data = await tools.importId(this.id)
        this.$router.push('/recipe/' + data.id)
      } catch (exc) {
        console.error(exc)
        this.$toast.error('Failed to import recipe.')
      }
      this.$toast.success('Recipe imported')
    },
    ingredientQuantity (ingredient) {
      return Math.round(ingredient.quantity * this.quantityScale * 100) / 100
    }
  },
  computed: {
    owner () {
      return this.$user.loggedIn() && this.data.author.email === this.$user.data.email
    }
  }
}
</script>

<style scoped>
ul {
  margin-block-start: 0px;
  margin-block-end: 0px;
}
#ingredients-card {
  margin: 0px 10px 20px 10px;
}
#description {
  font-family: Roboto;
  white-space: pre-wrap;
}
</style>
