import axios from 'axios'

export default {
  uuid4 () {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      /* eslint-disable */
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8)
      /* eslint-enable */
      return v.toString(16)
    })
  },
  async importId (id) {
    let data = (await axios.get('/backend/recipes/' + id + '/')).data

    let imageFormData = null
    if (data.image) {
      imageFormData = new FormData()
      let imageBlob = new Blob([(await axios.get(data.image, {responseType: 'blob'})).data])
      imageFormData.append('image', imageBlob, this.uuid4() + '.png')
    }
    if (data.image !== undefined) {
      delete data.image
    }

    data = (await axios.post('/backend/recipes/', data)).data
    if (imageFormData) {
      await axios.patch(data.url, imageFormData)
    }
    return data
  }
}
