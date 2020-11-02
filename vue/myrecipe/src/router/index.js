import Vue from 'vue'
import Router from 'vue-router'
import RecipeList from '@/components/RecipeList'
import RecipeDetails from '@/components/RecipeDetails'
import EditRecipe from '@/components/EditRecipe'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      redirect: '/recipe-list'
    },
    {
      path: '/recipe-list',
      name: 'RecipeList',
      component: RecipeList
    },
    {
      path: '/recipe/:id',
      name: 'RecipeDetails',
      component: RecipeDetails,
      props: true
    },
    {
      path: '/new-recipe',
      name: 'NewRecipe',
      component: EditRecipe
    },
    {
      path: '/edit-recipe/:editId',
      name: 'EditRecipe',
      component: EditRecipe,
      props: true
    }
  ]
})
