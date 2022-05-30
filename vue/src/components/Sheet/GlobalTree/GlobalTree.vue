<template>
  <div>
    <v-item-group mandatory v-model="mode">
      <v-item
          v-for="n in [0,1,2]"
          :key="n"
          v-slot="{ active, toggle }"
      >
        <v-chip
            active-class="blue--text"
            small
            :input-value="active"
            @click="toggle"
        >
          {{ ['k','l','t'][n] }}
        </v-chip>
      </v-item>
    </v-item-group>
    {{ $t('page2.description1') }} {{quasiNum}}
    <br/>
    {{ $t('page2.description2') }} {{riskNum}} / {{this.treeRoot? this.treeRoot.count:0}}
    <br/>
    {{ $t('page2.description3') }} {{cer}}
    <svg ref="svg" style="height: 300px; width: 100%;"
         :viewBox="`${-width / 2}, ${-height / 2}, ${width}, ${height}`">
      <g id="treeGroup"></g>
    </svg>
    <v-slider
        v-model="threshold"
        :max="max"
        :color="colorMin"
        :track-color="colorMax"
        min="1"
        hide-details
    >
      <template v-slot:prepend>
        <v-menu
            :close-on-content-click="false"
            offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
                icon
                color="primary"
                dark
                v-bind="attrs"
                v-on="on"
            >
              <v-icon>mdi-eyedropper-variant</v-icon>
            </v-btn>
          </template>
          <v-color-picker
              v-model="colorMin"
              hide-canvas
          ></v-color-picker>
          <v-color-picker
              v-model="colorMax"
              hide-canvas
          ></v-color-picker>
        </v-menu>
      </template>
      <template v-slot:append>
        <v-text-field
            v-model="threshold"
            class="mt-0 pt-0"
            hide-details
            single-line
            type="number"
            style="width: 60px"
        ></v-text-field>
      </template>
    </v-slider>
  </div>

</template>

<script>
import * as d3 from 'd3'
let time = null;
export default {
  name: "GlobalTree",
  data(){
    return {
      threshold: 0,
      width: 1080,
      height: 800,
      mode: 0,
      colorMin: "#E82424FF",
      colorMax: "#1C9DF3FF",
      riskNum: 0, // 可能暴露的数据条目
      quasiNum: 0, // 违背k匿名的组合数
    }
  },
  props:{
    treeRoot: Object, // 规定类型，传递静态or动态值
    cer: String, // 风险值
  },
  computed:{
    max(){
      // max获取当前webTree中结点对应模式的最大值，如最大k值，获取调节栏目的范围
      return this.parseData ? d3.max(this.parseData, d=>this.temp(d))[0] : 0
    },
    parseData(){
      return this.parseTree(this.treeRoot, [], 0, 2 * Math.PI, 50, "A", true)
    },
  },
  methods: {
    parseTree(root, data, sA, eA, sR, parentID, IsSafe){
      let risk = false;
      // webTree结点 存有webTree圆环的数据 起始度数 结束度数 起始半径 ID名
      if(!root) return null // 如果webTree根为空，即没有webTree，所以返回空
      let children = root.children
      let b = 0;
      let sum = 0
      children.forEach(child => {
        b += child.branch   // 每个节点自己就有branch和count，为什么还要去遍历子节点的
        sum += child.count  // count是当前节点下有多少条数据
      })
      let st = sA
      b = (eA - sA) / b    // 将属于这个属性的圆弧划分为b份，每个分类占多少度，branch的意思是这个节点的子路径条数，每个子路径都是一个类别组合，圆中每个类别占度数一致
      sum = 20 / sum       // 每次都是把20环宽分给各个条目，每次只跟当下比，所以每个圆环弧都会有一段比较宽，而且圆环弧环宽-20后加在一起都一样为20
      if (IsSafe && root.content.k < this.threshold){
        this.riskNum += root.count;
        IsSafe = false;
      }
      children.forEach(child => {
        if (child.content.k < this.threshold) {
          risk = true;
          //console.log(child.content.k, parentID);
        }
        let x0 = st                           // 开始的弧度数
        let x1 = st + b * child.branch        // 这个child结束的弧度数，根据child拥有的子路径数目确定
        let y0 = sR                           // 起始半径
        let y1 = sR + 20 + sum * child.count  // 结束半径，确保每个圆环弧的环宽至少是20，然后根据该子节点条目数扩大
        let id = `${parentID}-${child.labels}`// id命名
        //console.log(id)
        data.push({x0,x1,y0,y1,id,k: child.content.k, l: child.content.l, t: child.content.t})
        this.parseTree(child, data, x0, x1, y1, id, IsSafe)
        st = x1                               // 更新弧度基数为上一个圆弧的结束弧度
      })
      if (risk) this.quasiNum = this.quasiNum + 1;
      return data
    },
    temp(d) {
      if(this.mode === 0) return d.k;
      if(this.mode === 1) return d.l;
      if(this.mode === 2) return d.t;
    },
    reRender() {
      // 要记得归0，不然风险值会累加
      this.quasiNum = 0;
      this.riskNum = 0;
      //console.log('reRender')
      if(!this.treeRoot) return
      const vue = this;
      let linear = d3.scaleLinear().domain([0, this.threshold]).range([0, 1]).clamp(true);
      let compute = d3.interpolateRgb(this.colorMin, this.colorMax)
      let arc = d3
          .arc()
          .startAngle(d => d.x0)
          .endAngle(d => d.x1)
          .padAngle(1 / 200)
          .padRadius(200)
          .innerRadius(d => d.y0 + 1)
          .outerRadius(d => d.y1 - 1)
      let arcs = d3.select(this.$refs.svg).select('#treeGroup')
          .selectAll(".tree")
          .data(this.parseData)
          .join("path")
          .attr("id", d => d.id)
          .attr("class", "tree")
          .attr("d", arc)
          .attr("fill", d=>compute(linear(this.temp(d))))
      // 用计时器来区分单双击
      arcs.on('dblclick', function (){
        clearTimeout(time);
        console.log('dblclick');
        //console.log(vue.threshold);
        let data={
          pathID: this.id,
          threshold: vue.threshold
        };
        vue.$emit('quickMerge', data);
      })
      arcs.on('click', function () {
        clearTimeout(time);
        time = setTimeout(() => {
          // 这里是点击处
          // console.log(this.id);
          console.log('Concentrate on', this.id);
          let data={
            highlightID: this.id
          };
          vue.$emit('changeID', data); // 事件触发后，自动触发父组件的changeID事件
        } , 300)
      })
    },
  },
  mounted() {
    this.reRender();
  },
  watch: {
    // 如果treeRoot发生变化就调用reRender
    treeRoot(){
      // 树变化后变化
      //console.log('treeRoot reRender')
      this.reRender()
    },
    threshold(){
      // 调节阈值后变化
      this.reRender()
    },
    mode(){
      // 调节模式后变化
      this.reRender()
    },
  },
  // updated() {
  //   // 数据更新时调用，如果用这个quasiNum归0时数据也变了，会无限循环
  //   console.log('updated reRender')
  //   this.reRender()
  // }
}
</script>

<style scoped>

</style>