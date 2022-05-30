<template>
  <v-app id="app" onselectstart="return false">
    <link href="https://fonts.googleapis.com/css?family=Roboto:100,300,400,500,700,900" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/@mdi/font@4.x/css/materialdesignicons.min.css" rel="stylesheet">
    <v-tabs fixed-tabs dark style="flex: none" color="#FFC0CBFF">
      <v-tab @click="route('/introduce')">{{ $t('title.page0') }}</v-tab>
      <v-tab @click="route('/upload')">{{ $t('title.page1') }}</v-tab>
      <v-tab @click="route('/privacy')">{{ $t('title.page2') }}</v-tab>
      <v-tab @click="route('/utility')">{{ $t('title.page3') }}</v-tab>
      <v-tab @click="route('/release')">{{ $t('title.page4') }}</v-tab>
      <button type="button" class="btn btn-success" @click="changeLocale">中文/EN</button>
    </v-tabs>
    <router-view></router-view>
  </v-app>
</template>

<script>

export default {
  name: 'App',
  components: {},
  methods: {
    route(path){
      if (this.$route.path === path) return
      this.$router.push(path)
    },
    changeLocale () {
      this.$vuetify;
      let locale = this.$i18n.locale
      locale === 'zh' ? this.$i18n.locale = 'en' : this.$i18n.locale = 'zh'
    },
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.solid{
  border-style: solid;
  border-color: red;
}
</style>
