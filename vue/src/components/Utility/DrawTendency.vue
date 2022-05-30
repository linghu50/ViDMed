<template>
  <!--必须设置echarts的宽跟高，不然不显示-->
  <div id="chartLineBox" style="width: 90%;height: 50vh;"> </div>
</template>

<script>
import * as echarts from 'echarts'
import {mapState} from "vuex";
export default {
  name: "DrawTendency",
  computed: {
    ...mapState([
      'headers',
      'fileName',
      'targets',
      'history',
    ]),
  },
  mounted() {
    this.chartLine = echarts.init(document.getElementById('chartLineBox'));
    let xdata=[];
    let accuracyData = [];
    let riskData = [];
    this.history.forEach(h => {
      xdata.push(this.$i18n.t('history.state')[h.action[0]]);
      accuracyData.push(h.accuracy)
      riskData.push(h.risk)
    })

    // 指定图表的配置项和数据
    let option = {
      tooltip: {              //设置tip提示
        trigger: 'axis'
      },

      legend: {               //设置区分（哪条线属于什么）
        data: [this.$i18n.t('page3.label1'), this.$i18n.t('page3.label2')],
      },
      color: ['#8AE09F', '#FA6F53'],       //设置区分（每条线是什么颜色，和 legend 一一对应）
      xAxis: {                //设置x轴
        type: 'category',
        boundaryGap: false,     //坐标轴两边不留白
        data: xdata,
        //data: ['update', 'merge', 'merge', 'merge', 'merge', 'merge', 'merge','merge'],
        name: this.$i18n.t('page3.labelx'),           //X轴 name
        nameTextStyle: {        //坐标轴名称的文字样式
          color: '#FA6F53',
          fontSize: 16,
          padding: [0, 0, 0, 20]
        },
        axisLine: {             //坐标轴轴线相关设置。
          lineStyle: {
            color: '#FA6F53',
          }
        }
      },
      yAxis: {
        name: this.$i18n.t('page3.labely'),
        scale: true,
        nameTextStyle: {
          color: '#FA6F53',
          fontSize: 16,
          padding: [0, 0, 10, 0]
        },
        axisLine: {
          lineStyle: {
            color: '#FA6F53',
          }
        },
        type: 'value'
      },
      series: [
        {
          name: this.$i18n.t('page3.label1'),
          //data: [0.583, 0.622, 0.572, 0.563, 0.552, 0.551, 0.549, 0.543],
          data: accuracyData,
          type: 'line',               // 类型为折线图
          lineStyle: {                // 线条样式 => 必须使用normal属性
            normal: {
              color: '#8AE09F',
            }
          },
        },
        {
          name: this.$i18n.t('page3.label2'),
          //data: [0.9566, 0.8882, 0.7964, 0.7482, 0.6778, 0.6041, 0.5449, 0.4432],
          data: riskData,
          type: 'line',               // 类型为折线图
          lineStyle: {                // 线条样式 => 必须使用normal属性
            normal: {
              color: '#FA6F53',
            }
          },
        },
      ]
    };

    // 使用刚指定的配置项和数据显示图表。
    this.chartLine.setOption(option);
  },
}
</script>

<style scoped>

</style>