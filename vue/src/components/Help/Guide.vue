<template>
  <div>
    <p v-html="$t('help')[this.tip][this.help]"> </p>
    <v-card-actions style="height:fit-content;width: fit-content" v-if="show1()">
      <v-btn outlined rounded text @click="changeForward()">{{ $t('help.button1') }}</v-btn>
      <v-btn outlined rounded text @click="changeBack(help)">{{ $t('help.button2') }}</v-btn>
    </v-card-actions>
  </div>

</template>

<script>
import {mapState} from "vuex";

export default {
  name: "Guide",
  props:{
    tip: String, // 规定类型，传递静态or动态值,tip代表当前页面
  },
  computed:{
    ...mapState([
        'help', //help表示对应的提示操作
    ]),
  },
  methods:{
    show1(){
      //console.log("show", this.tip === 'page3' && this.help === 'page2')
      return (this.tip === 'page3' || this.tip === 'page4') && this.help === 'page2';
    },
    changeForward(){
      this.$store.state.help = 'operation';
    },
    changeBack(help){
      let path = {'page1': '/upload', 'page2': '/privacy', 'page3': '/utility', 'page4': '/release'};
      this.$router.push(path[help]);
    },

  }
}
</script>

<style scoped>

</style>