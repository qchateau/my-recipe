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
        <v-card id="ingredients-card" v-if="data.ingredients.length > 0" style="min-height: 45px">
          <div style="float: right; margin: 5px"></div>
          <ul>
            <li
              v-for="ingredient in data.ingredients"
              :key="ingredient.id"
            >{{ Math.round(ingredient.quantity * quantityScale * 100) / 100 }} {{ ingredient.unit }} {{ ingredient.name }}</li>
          </ul>
        </v-card>
        <div>{{ data.description }}</div>
      </v-card-text>

      <v-speed-dial v-model="fab" bottom right fixed>
        <template v-slot:activator>
          <v-btn v-model="fab" color="blue darken-2" dark fab>
            <v-icon v-if="fab">mdi-close</v-icon>
            <v-icon v-else>mdi-pencil</v-icon>
          </v-btn>
        </template>
        <v-btn fab dark small color="indigo" @click="scaleDrawer = !scaleDrawer">
          <v-icon>mdi-scale</v-icon>
        </v-btn>
        <v-btn fab dark small color="green" @click="$router.push('/edit-recipe/'+id+'/')">
          <v-icon>mdi-playlist-edit</v-icon>
        </v-btn>
        <v-btn fab dark small color="red" @click="onDelete">
          <v-icon>mdi-delete</v-icon>
        </v-btn>
      </v-speed-dial>
    </div>

    <v-navigation-drawer v-model="scaleDrawer" absolute temporary bottom height="30%">
      <div style="margin: 10px">
        <h3>Scale quantities</h3>
        <v-text-field v-model="quantityScale" hide-details single-line type="number" />
      </div>
    </v-navigation-drawer>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RecipeDetails',
  props: ['id'],
  data () {
    return {
      data: null,
      quantityScale: 1,
      scaleDrawer: false,
      fab: false
    }
  },
  async mounted () {
    this.data = (await axios.get('/backend/recipes/' + this.id + '/')).data
  },
  methods: {
    async onDelete () {
      try {
        await this.$confirm('This will permanently delete the recipe. Continue ?', 'Warning', {
          confirmButtonText: 'OK',
          cancelButtonText: 'Cancel',
          type: 'warning'
        })
      } catch (exc) {
        return
      }

      try {
        await axios.delete('/backend/recipes/' + this.id + '/')
        this.$toast.success('Recipe deleted.')
        this.$router.push('/')
      } catch (exc) {
        this.$toast.error('Failed to delete recipe.')
      }
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
#recipe-header {
  text-align: center;
}
</style>
