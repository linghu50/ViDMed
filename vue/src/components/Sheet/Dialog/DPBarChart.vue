<template>
  <v-card elevation="10"
          class="mb-6 ml-6"
          :width="width">
    <v-toolbar
        dark
        color="gray"
    >
      <v-toolbar-title>{{ title }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items>
        <v-container
            fluid
            class="px-0"
        >
          <v-switch
              v-model="hover"
              class="mt-2"
              :label="`${$t('dp.button2')} ${hover ? $t('dp.choice1'): $t('dp.choice2')}`"
          ></v-switch>
        </v-container>
      </v-toolbar-items>
    </v-toolbar>

      <svg :width="width" :height="height" style="background-color: whitesmoke">
        <g ref="chart"></g>
        <g ref="outline"></g>
        <transition name="fade">
          <g v-show="hover" >
            <rect x="0" :y="2" :width="width" :height="height - 4" fill="black" opacity="0.6"></rect>
            <g ref="lambda"></g>
            <g ref="lambda"></g>
            <text x ="5" :y="50" fill="white" dominant-baseline="middle">lambda</text>
          </g>
        </transition>

        <text ref="tooltip" visibility="hidden" text-anchor="middle"></text>

      </svg>

  </v-card>
</template>

<script>
import * as d3 from "d3";
import {laplaceCDF, laplaceNoise} from "../../../plugins/mathUtils";
import {mapState, mapGetters, mapMutations} from "vuex";
import {mlAxios} from "../../../plugins/machineLearning";

export default {
  name: "DPBarChart",
  data() {
    return {
      hover: false,
      lambda: [0],  // 加噪参数列表
      width: 900,
      height: 180,
      cer: null,
    }
  },
  props: {
    index: Number,  // 属性序号
    aggSize: Number,  // slider个数
    cerSchema: Array,
  },
  computed: {
    ...mapGetters([
        'tData'
    ]),
    ...mapState([
      'schema',
      'headers',
      'selectedRow',
      'mapSchema',
    ]),
    title(){
      return this.headers[this.index].value
    },
    data(){
      let result = []
      this.selectedRow.forEach(row=>result.push(row[this.headers[this.index].value]))
      return result
    },
    CDF(){
      // 加噪变化量
      let cdf = new Array(this.lambda.length).fill(0)
      for (let i = 0; i < this.lambda.length; i++) {
        // todo: lambda中记录的是点的纵坐标变化量，要将其转化回原始的lambda，研究一下怎么转变
        let l = Math.abs(this.lambda[i]) * 2 / (this.height) * this.agg[i]
        if (l > 0) {
          for (let j = 0; j < this.lambda.length; j++) {
              let d = Math.abs(j - i);
              let F1 = laplaceCDF(0, l, d * this.dur)
              let F2 = laplaceCDF(0, l, (d + 1) * this.dur)
              if (j !== i) {
                cdf[j] += (F2 - F1) * this.agg[i];
              } else {
                cdf[j] -= (1 - F2 + F1) * this.agg[i];
              }
          }
        }
      }
      return cdf
    },
    min() {
      return d3.min(this.data)
    },
    max() {
      return d3.max(this.data)
    },
    dur() {
      // 平均间隔
      return (this.max - this.min) / this.aggSize
    },
    agg() {
      // 统计选中的待加噪数据落在每个区间的数目
      let data = new Array(this.aggSize).fill(0)
      this.data.forEach(d => {
        let index = Math.floor((d - this.min) / this.dur);
        data[index === this.aggSize ? this.aggSize - 1 : index] += 1
      })
      return data;
    },
    chartW() {
      return this.width - 100;
    },
    chartH() {
      return this.height - 20;
    }
  },
  methods: {
    ...mapMutations([
      'pushTData',
    ]),
    async saveNoise() {
      let newTData = [...this.tData]
      let update = false
      let _this = this
      this.selectedRow.forEach(row => {
        // 将数值转为所落区间序号
        let label = _this.headers[_this.index].value
        let index = Math.floor((row[label] - _this.min) / _this.dur)
        index = index === _this.aggSize ? _this.aggSize - 1 : index
        if (_this.lambda[index] !== 0) {
          // 产生拉普拉斯随机数
          let dp = laplaceNoise(0, _this.lambda[index])
          if (dp !== 0) {
            let newRow = window.deepCopy(row)
            // 加噪
            newRow[label] += dp
            newRow[label] = Number(newRow[label].toFixed(3))
            newTData[newRow['_index']] = newRow
            update = true
          }
        }
      })
      if (update) {
        let headers = [];
        //console.log(this.headers);
        this.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push(h.value));
        const tHeader = headers;
        const tableData = newTData;
        const filename = null;
        let choose = [];
        this.$store.state.historyLeft.forEach(e => {choose.push(e.name)})
        await this.getAccuracy({
          "tHeader": tHeader,
          "tData": tableData,
          "filename": filename,
          "choose": choose,
          "DownFile": false,
          "target": tHeader[tHeader.length - 1],
          "className": this.mapSchema[this.mapSchema.length -1].y,
          "language": this.$i18n.locale
        });
        await this.getCer();
        console.log(this.cer);
        this.pushTData({action: ["DP", "dp"], tData: newTData, accuracy:this.accuracy, risk: this.cer})
      }
    },
    getAccuracy(data){
      let vue = this;
      return new Promise((resolve,reject) => {
        mlAxios.post("getDecision", data, {timeout: 200000})
            .then(res => {
              console.log(res);
              vue.accuracy = res['data']['accuracy'];
              console.log('await',vue.accuracy)
              resolve(res)
            }).catch(err => reject(err))
      })
    },
    getCer() {
      let data = {
        schema: this.cerSchema,
      }
      let vue = this;
      console.log('cerSchema:', this.cerSchema);
      return new Promise((resolve,reject) => {
        this.$http.post('privacyAssess', data).then(res => {
            if (res.data.code === 200) {
              vue.cer = res.data.data;
              resolve(res)
            }
        }).catch(err=>reject(err))
      })
    },

    drawParameter(svg, p, y) {
      // 绘制白色的lambda线，且允许拖拽修改
      let drawLine = () => {
        svg.selectAll('line')
            .data(new Array(p.length - 1))
            .join('line')
            .attr('x1', (d, i) => (i + 0.5) * this.chartW / p.length + 50)
            .attr('x2', (d, i) => (i + 1.5) * this.chartW / p.length + 50)
            .attr('y1', (d, i) => y - p[i])
            .attr('y2', (d, i) => y - p[i + 1])
            .attr('stroke-width', 2)
            .attr('stroke', 'whitesmoke')
      };
      // 绘制lambda曲线
      drawLine()
      let _this = this;
      // 实现拖拽lambda曲线上点完成值修改
      svg.selectAll('circle')
          .data(p)
          .join('circle')
          .attr('cx', (d, i) => (i + 0.5) * this.chartW / p.length + 50) // i+0.5是让点居中，+50是留出左侧的空白
          .attr('cy', (d, i) => y - p[i]) // 由整体居中位置-lambda
          .attr('r', 5)
          .attr('fill', 'whitesmoke')
          .attr('stroke', 'gray')
          .attr('stroke-width', 2)
          .each(function (d, i) {
            d3.select(this).call(d3.drag()
                .on('drag', function (e) {
                  let dom = d3.select(this)
                  let now = Number(dom.attr('cy'));
                  // e.dy表示在垂直方向上的移动，即原纵坐标值+移动值在2到高度-4之间
                  if (now + e.dy > 2 && now + e.dy < _this.height - 4) {
                    // 赋值为移动后值
                    dom.attr('cy', now + e.dy)
                    // 点向上移动，lambda下降
                    _this.$set(p,i,p[i]-e.dy)
                    // p[i] -= e.dy
                    drawLine()
                    _this.drawOutLine()
                  }
                }))
          })
    },
    updateParameter() {
      // 更新lambda长度
      if (this.lambda.length !== this.aggSize) {
        let newLambda = new Array(this.aggSize).fill(0);
        // let oldD = 1 / this.lambda.length
        // let newD = 1 / this.aggSize
        // for (let i = 0; i < this.aggSize; i++) {
        //   let indexNext = Math.floor((newD / oldD) * (i + 1))
        //   let indexLast = indexNext - 1
        //   let big = indexNext >= this.lambda.length ? this.lambda[this.lambda.length - 1] : this.lambda[indexNext]
        //   let small = indexLast < 0 ? this.lambda[0] : this.lambda[indexLast]
        //   let left = newD * (i + 1 / 2) - oldD * (indexLast + 1 / 2)
        //   let right = (1 - newD * (i + 1 / 2)) - (1 - oldD * (indexNext + 1 / 2))
        //   newLambda.push(small * Math.abs(left / (left + right)) + big * Math.abs(right / (left + right)))
        // }
        this.lambda = newLambda
      }
      // d3.select(this.$refs.lambda)是选择ref为lambda的第一个元素，即31行的<g>
      this.drawParameter(d3.select(this.$refs.lambda), this.lambda, this.height / 2)
    },
    drawOutLine(){
      // 我们在制作柱状图时，不能确定数据的变化范围，或者数据变化过大，就可以使用比例尺scaleLinear，把一组数据映射到一个集合中
      // 将每个分段的数目映射到[0,160]
      let linear = d3.scaleLinear()
          .domain([0, d3.max(this.agg)]) // 要被映射的数据范围， 即原始数据
          .range([0, this.chartH - 20]) // 要被映射到的数据
      // 为outline添加有序列表
      // Todo 绘制红色直线，代表可能的加噪结果？
      d3.select(this.$refs.outline).selectAll('.ol1')
          .data(this.CDF)
          .join('line')
          .attr('class', 'ol1')
          .attr('x1', (d, i) => (i + 0.5) * this.chartW / this.aggSize + 50)
          .attr('y1', (d, i) => this.chartH - linear(this.agg[i] - d))
          .attr('x2', (d, i) => (i + 0.5) * this.chartW / this.aggSize + 50)
          .attr('y2', (d, i) => this.chartH - linear(this.agg[i] + d))
          .attr('stroke-width', 1)
          .attr('stroke', 'red')
    },
    drawChart() {
      let _this = this;
      let linear = d3.scaleLinear().domain([0, d3.max(this.agg)]).range([0, this.chartH - 20])
      d3.select(this.$refs.chart).selectAll('line')
          .data([1])
          .join('line')
          .attr('x1', 0)
          .attr('x2', this.width)
          .attr('y1', this.chartH)
          .attr('y2', this.chartH)
          .attr('stroke-width', 3)
          .attr('stroke', 'gray')
      let selection = d3.select(this.$refs.chart).selectAll('rect')
          .data(this.agg)
          .join('rect')
          .attr('fill', 'blue')
          .attr('opacity', 0.5)
          .attr('x', (d, i) => i * this.chartW / this.agg.length + 50)
          .attr('width', this.chartW / this.agg.length - 4)
          .attr('y', this.chartH)
          .attr('height', 0)
          .on('mouseover', function(e, d) {
            const node = selection.nodes();
            d3.select(this).attr('opacity', 1)
            const i = node.indexOf(this);
            d3.select(_this.$refs.tooltip)
                .attr('x', (i + 0.5) * _this.chartW / _this.agg.length + 50)
                .attr('y', _this.chartH - linear(d) - 5)
                .text(`${i}`)
                .attr('visibility', 'visible')
          })
          .on('mouseleave', function(){
            d3.select(this).attr('opacity', 0.5)
            d3.select(_this.$refs.tooltip)
                .attr('visibility', 'hidden')
          })
          .transition()
          .attr('y', d => this.chartH - linear(d) - 2)
          .attr('height', d => linear(d))
      let text;
      text = new Array(Math.min(this.aggSize + 1, 10))
      let dur = (this.max - this.min) / (text.length - 1)
      for (let i = 0; i < text.length; i++) {
        text[i] = this.min + i * dur
      }
      d3.select(this.$refs.chart).selectAll('text')
          .data(text)
          .join('text')
          .attr('text-anchor', 'middle')
          .attr('y', this.chartH + 16)
          .attr('x', (d, i) => i * this.chartW / (text.length - 1) + 50)
          .text(d => d.toFixed(1))
      this.drawOutLine()
    }
  },
  mounted() {
    this.updateParameter()
    this.drawChart()
  },
  watch: {
    data() {
      this.updateParameter()
      this.drawChart()
    },
    aggSize() {
      this.updateParameter()
      this.drawChart()
    }
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>