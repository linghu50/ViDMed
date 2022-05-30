<template>
  <div class="stock">
    <svg ref="svg" :width="width" :height="height">
      <rect :width="width * (value / max)" :height="height" fill="lightblue">
      </rect>
      <text dy="1em">
        {{value}}
      </text>
    </svg>
  </div>
</template>

<script>
export default {
  name: "NumberStock",
  props: {
    value: Number,
    max: Number,
    width: Number,
    height: Number,
  },
  created: function () {
  }
}
</script>

<style scoped>
@import "../stock.css";
</style>