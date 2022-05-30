<template>
  <div class="d-flex">
<!--    <div class="col-2 p-0">-->
    <div class="col-2 pt-0 pr-0">
      <v-card elevation="4" shaped tile class="p-lg-2 m-2" style="width: initial">
        <v-card-title>{{$t('history.title')}}</v-card-title>
        <v-list dense style="height: 300px;" class="overflow-auto">
          <v-list-item-group
              :value="this.currentIndex"
              @change="selectHistory"
              mandatory
              color="primary">
            <v-list-item v-for="(item, i) in this.history" :key="i">
              <v-list-item-action>
                <v-chip :color="
                item.action[0]==='Base' ? 'primary':
                item.action[0]==='Merge' ? 'red':
                item.action[0]==='DP' ? 'green':'secondary'"
                        text-color="white">{{$t('history.state')[item.action[0]]}}</v-chip>
              </v-list-item-action>
              <v-list-item-content>
                <v-list-item-title v-text="$t('history.action')[item.action[1]]"></v-list-item-title>
              </v-list-item-content>
              <v-list-item-avatar>
                <!-- 添加趋势图标 -->
                <font-awesome-icon :icon="['fas', 'long-arrow-up']" style="color:green;" v-if="i>0&&item.accuracy>history[i-1].accuracy"></font-awesome-icon>
                <font-awesome-icon :icon="['fas', 'long-arrow-down']" style="color:red;" v-if="i>0&&item.accuracy<history[i-1].accuracy"></font-awesome-icon>
                <font-awesome-icon :icon="['fas', 'minus']" style="color:deepskyblue;" v-if="i>0&&item.accuracy==history[i-1].accuracy">—</font-awesome-icon>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title v-text="item.accuracy"></v-list-item-title>
              </v-list-item-content>
              <v-list-item-avatar>
                <!-- 添加趋势图标 -->
                <font-awesome-icon :icon="['fas', 'long-arrow-up']" style="color:green;" v-if="i>0&&item.risk>history[i-1].risk"></font-awesome-icon>
                <font-awesome-icon :icon="['fas', 'long-arrow-down']" style="color:red;" v-if="i>0&&item.risk<history[i-1].risk"></font-awesome-icon>
                <font-awesome-icon :icon="['fas', 'minus']" style="color:deepskyblue;" v-if="i>0&&item.risk==history[i-1].risk">—</font-awesome-icon>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title v-text="item.risk"></v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-card>
      <v-card elevation="4" shaped tile class="p-lg-2 m-2" style="width: initial">
        <v-card-title> {{$t('help.title')}} </v-card-title>
        <Guide :tip="tip"> </Guide>
      </v-card>
    </div>
    <div>
      <div>
        <v-card elevation="4" shaped tile class="p-lg-2 m-2" style="width: 300px">
          <v-card-title>{{ $t('page3.cardTitle2') }}</v-card-title>
          <UtilityDecisionTree @getTarget="changeTarget"
                               @showHeatmap="getHeatmap"
                               @showKNN="getKNN"
                               @showLogistic="getLogistic"
                               @showDecision="getDecision"
                               @showCompare="getCompare"> </UtilityDecisionTree>
        </v-card>
      </div>
    </div>
    <div class="pt-0 pr-0" style="height:100%;width: 100%">
      <div>
        <v-card elevation="4" shaped tile class="p-lg-2 m-2" style="height: 50%; width: 95%">
          <v-card-title>{{ $t('page3.cardTitle4') }}</v-card-title>
          <DrawTendency> </DrawTendency>
        </v-card>
      </div>

      <div>
        <v-card v-if="showTree" shaped tile class="p-lg-2 m-2" style="height: 50%; width: 95%">
          <v-card-title>{{ $t('page3.cardTitle3') }}</v-card-title>
          <ShowDecisionTree :target = 'target'> </ShowDecisionTree>
        </v-card>
        <v-card v-if="showHeatmap" shaped tile class="p-lg-2 m-2" style="height: 50%; width: 95%">
<!--          <v-card-title>{{ $t('page3.cardTitle3') }}</v-card-title>-->
          <v-card-title>{{$t('page3.Heatmap')}}</v-card-title>
          <img :src="srcHeatmap" alt="相关性热力图" style="height:50%;width:50%;"/>
        </v-card>

        <v-card v-if="showKNN" shaped tile class="p-lg-2 m-2" style="height: 50%; width: 95%;">
          <!--          <v-card-title>{{ $t('page3.cardTitle3') }}</v-card-title>-->
          <v-card-title>{{$t('page3.KNN')}}</v-card-title>
          <img :src="srcKNN" alt="混淆矩阵&ROC" style="height:80%;width:90%;"/>
        </v-card>

        <v-card v-if="showLogistic" shaped tile class="p-lg-2 m-2" style="height: 50%; width: 95%">
          <!--          <v-card-title>{{ $t('page3.cardTitle3') }}</v-card-title>-->
          <v-card-title>{{$t('page3.Logistic')}}</v-card-title>
          <img :src="srcLogistic" alt="混淆矩阵&ROC" style="height:80%;width:90%;"/>
        </v-card>

        <v-card v-if="showDecision" shaped tile class="p-lg-2 m-2" style="height: 50%; width: 95%">
          <!--          <v-card-title>{{ $t('page3.cardTitle3') }}</v-card-title>-->
          <v-card-title>{{$t('page3.Decision')}}</v-card-title>
          <img :src="srcDecision" alt="混淆矩阵&ROC" style="height:80%;width:90%;"/>
        </v-card>
        <v-card v-if="showCompare" shaped tile class="p-lg-2 m-2" style="height: 50%; width: 95%">
          <!--          <v-card-title>{{ $t('page3.cardTitle3') }}</v-card-title>-->
          <v-card-title>{{$t('page3.Comparison')}}</v-card-title>
          <img :src="srcConfusion" alt="混淆矩阵" style="height:80%;width:90%;"/>
          <img :src="srcROC" alt="ROC" style="height:80%;width:90%;"/>
        </v-card>

      </div>
    </div>

  </div>
</template>

<script>
import {mapState, mapMutations, mapGetters} from 'vuex'
//import UtilityMatrix from "./UtilityMatrix";
//import DP2DChart from "../Sheet/Dialog/DP2DChart";
import UtilityDecisionTree from "./UtilityDecisionTree";
import ShowDecisionTree from "./ShowDecisionTree";
import Guide from "../Help/Guide"
import DrawTendency from "./DrawTendency";
export default {
  name: "UtilityAnalysis",
  components: {DrawTendency, UtilityDecisionTree, ShowDecisionTree,Guide},
  data(){
    return{
      s1:0,
      s2:0,
      tip: 'page3',
      target: null,
      showHeatmap: false,
      showKNN: false,
      showLogistic: false,
      showDecision: false,
      showTree: false,
      showCompare: false,
      srcHeatmap: null,
      srcKNN: null,
      srcLogistic : null,
      srcDecision: null,
      srcConfusion: null,
      srcROC: null,
    }
  },
  computed: {
    ...mapGetters([
        'headersName',
        'tData',
    ]),
    ...mapState([
        'headers',
        'fileName',
        'schema',
        'history',
        'currentIndex',
    ]),
    y() {
      let y = []
      for (let s of this.schema) {
        if (this.headers[s].type in [0, 1]) {
          // todo 这里把数值属性和分类属性放到一起了，要重新定义分类属性的距离计算
          y.push(s)
        }
      }
      return y
    },
  },
  methods: {
    ...mapMutations([
        'setObj',
        'pushTData',
        'setToken'
    ]),
    showClean(){
      this.showHeatmap = false;
      this.showKNN = false;
      this.showLogistic = false;
      this.showDecision = false;
      this.showTree = false;
      this.showCompare = false;
    },
    changeTarget(target){
      this.target = target;
    },
    getHeatmap(src){
      this.showClean();
      this.showHeatmap = true;
      this.srcHeatmap = src;
    },
    getKNN(src){
      this.showClean();
      this.showKNN = true;
      this.srcKNN= src;
    },
    getLogistic(src){
      this.showClean();
      this.showLogistic = true;
      this.srcLogistic= src;
    },
    getDecision(src) {
      this.showClean();
      this.showDecision = true;
      this.srcDecision = src;
      this.showTree = true;
    },
    getCompare(src1, src2) {
      this.showClean();
      this.srcConfusion = src1;
      this.srcROC = src2;
      this.showCompare = true;
    },
    selectHistory(e){
      const modify = {}
      let newTData = this.history[e].tData;
      for (let i = 0; i < this.tData.length; i++) {
        if (newTData[i] !== this.tData[i]) {
          let clean = {}
          for (let header of this.headers) {
            clean[header.value] = newTData[i][header.value]
          }
          modify[i] = clean
        }
      }
      this.setObj({type:'currentIndex', value:e})
      let _this = this;
      this.$http.post('updateTableau', {
        modify
      }).then(res => {
        _this.itemsList.length = 0
        _this.setObj({type:'treeRoot', value:_this.handleList(_this.itemsList, res.data.data, [])})
        _this.setObj({type:'globalTreeRoot', value: res.data.data})
        // _this.setObj({type:'treeRoot', value:res.data.data})
      })
    },
  }
}
</script>

<style scoped>

</style>