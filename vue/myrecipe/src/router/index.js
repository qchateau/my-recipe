import Vue from 'vue'
import Router from 'vue-router'
import RecipeList from '@/components/RecipeList'
import RecipeDetails from '@/components/RecipeDetails'
import EditRecipe from '@/components/EditRecipe'
import ImportRecipe from '@/components/ImportRecipe'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      redirect: '/recipe-list',
      meta: {
        title: 'MyRecipe'
      }
    },
    {
      path: '/recipe-list',
      name: 'RecipeList',
      component: RecipeList,
      meta: {
        title: 'MyRecipe - List'
      }
    },
    {
      path: '/recipe/:id',
      name: 'RecipeDetails',
      component: RecipeDetails,
      props: true,
      meta: {
        title: 'MyRecipe'
      }
    },
    {
      path: '/new-recipe',
      name: 'NewRecipe',
      component: EditRecipe,
      meta: {
        title: 'MyRecipe - New'
      }
    },
    {
      path: '/edit-recipe/:editId',
      name: 'EditRecipe',
      component: EditRecipe,
      props: true,
      meta: {
        title: 'MyRecipe - Edit'
      }
    },
    {
      path: '/import-recipe/',
      name: 'ImportRecipe',
      component: ImportRecipe,
      meta: {
        title: 'MyRecipe - Import'
      }
    }
  ]
})
