<template>
  <div class="position-relative text-center">
    <v-chip
        class="ma-3"
        dark
        color="gray"
        label
    >
      {{headers[x].value}}
    </v-chip>
    <div>
      <template v-for="item in y" >
<!--         todo 这里把数值属性和分类属性放到一起了，要重新定义分类属性的距离计算-->
        <DotChart
            :key="item"
            class="mb-6"
            v-if="headers[x].type in [0,1]"
            :x="x"
            :y="item"
        ></DotChart>
        <BoxPlotChart
            :key="item"
            class="mb-6"
            v-else-if="headers[x].type in [0,1]"
            :x="x"
            :y="item"
        ></BoxPlotChart>
      </template>
    </div>
  </div>
</template>

<script>
import BoxPlotChart from "./BoxPlotChart";
import DotChart from "./DotChart";
import {mapState} from "vuex";
export default {
  name: "DP2DChart",
  components: {DotChart, BoxPlotChart},
  data() {
    return {

    }
  },
  props: {
    x: Number,
    y: Array
  },
  computed: {
    ...mapState([
      'schema',
      'headers',
      'selectedRow'
    ]),
  }
}
</script>

<style scoped>

</style>