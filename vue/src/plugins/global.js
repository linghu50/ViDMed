import Vue from 'vue'
export default {
    install () {
        Vue.prototype.$global = {
            mapType: ['Number', 'Categorical', 'Temporal', 'Spatial', 'Index'],
            //mapType: this.$t('page1.mapType'),
            dragged: null,
        }
    }
}