<template>
  <div>
    <UtilityLineDistance
        :inner="this.inner"
        :out="this.out"
    ></UtilityLineDistance>
    <UtilityLineDistribution
        :inner="this.inner"
        :out="this.out"
    ></UtilityLineDistribution>
  </div>
</template>

<script>
import UtilityLineDistance from "./UtilityLineDistance";
import UtilityLineDistribution from "./UtilityLineDistribution";
export default {
  name: "UtilityMatrix",
  components: {UtilityLineDistribution, UtilityLineDistance},
  data(){
    return{
    }
  },
  props: {
    inner: Number,
    out: Number,
  }
}
</script>

<style scoped>

</style>