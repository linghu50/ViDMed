<template>
  <div style="height:fit-content;width: fit-content">
    {{ $t('page3.description1') }}:
    <br/>
    <el-select v-model="target" clearable :placeholder="$t('page3.tip1')">
      <el-option
          v-for="item in targets"
          :key="item.id"
          :label="item.name"
          :value="item"></el-option>
    </el-select>
    <v-card-actions style="height:fit-content;width: fit-content">
      <v-btn outlined rounded text @click="getHeatMap(1)">{{ $t('page3.button1') }}</v-btn>
    </v-card-actions>
    <v-card-actions style="height:fit-content;width: fit-content">
      <v-btn outlined rounded text @click="getHeatMap(0)">{{ $t('page3.button2') }}</v-btn>
    </v-card-actions>

    <v-card-actions style="height:fit-content;width: fit-content">
      <v-btn outlined rounded text @click="getKNN(1)">{{ $t('page3.button3') }}</v-btn>
    </v-card-actions>
    <v-card-actions style="height:fit-content;width: fit-content">
      <v-btn outlined rounded text @click="getKNN(0)">{{ $t('page3.button4') }}</v-btn>
    </v-card-actions>

    <v-card-actions style="height:fit-content;width: fit-content">
      <v-btn outlined rounded text @click="getLogistic(1)">{{ $t('page3.button5') }}</v-btn>
    </v-card-actions>
    <v-card-actions style="height:fit-content;width: fit-content">
      <v-btn outlined rounded text @click="getLogistic(0)">{{ $t('page3.button6') }}</v-btn>
    </v-card-actions>

    <v-card-actions style="height:fit-content;width: fit-content">
      <v-btn outlined rounded text @click="getDecision(1)">{{ $t('page3.button7') }}</v-btn>
    </v-card-actions>
    <v-card-actions style="height:fit-content;width: fit-content">
      <v-btn outlined rounded text @click="getDecision(0)">{{ $t('page3.button8') }}</v-btn>
    </v-card-actions>

    <v-card-actions style="height:fit-content;width: fit-content">
      <v-btn outlined rounded text @click="getCompare(1)">{{ $t('page3.button9') }}</v-btn>
    </v-card-actions>

    <v-card-actions style="height:fit-content;width: fit-content">
      <v-btn outlined rounded text @click="getCompare(0)">{{ $t('page3.button10') }}</v-btn>
    </v-card-actions>

    <p v-if="show">
      {{MLmethod}}
      {{problem}} {{ $t('page3.description3')[0] }}<br />
      {{ $t('page3.description3')[1] }} {{showTarget}}<br />
      {{ $t('page3.description3')[2] }} {{useFeather}}<br />
    </p>
    <p v-if="show">
      {{ $t('page3.accuracy') }} :{{accuracy}}
    </p>
    <p v-if="show">
      {{ $t('page3.precision') }}: {{precision}}
    </p>
  <!--
  <v-card-actions style="height:fit-content;width: fit-content">
    <v-btn outlined rounded text @click="testPost(name)">Evaluate for ML</v-btn>
  </v-card-actions>
  -->
  </div>
</template>

<script>
import {mlAxios} from "../../plugins/machineLearning";
import {mapGetters, mapState} from "vuex";

export default {
  name: "UtilityDecisionTree",
  created() {
    this.$store.state.show = false;
  },
  data(){
    return{
      accuracy: 0,
      precision: 0,
      show: false,  // 展现得分
      problem: 0,
      useFeather: 0,
      target: null,
      showTarget: null,
      language: this.$i18n.locale,
      MLmethod: null,
    }
  },
  computed: {
    mapType(){
      return this.$global.mapType
    },
    loaded(){
      return this.headers.length > 0
    },
    ...mapGetters([
      'headersName',
      'tData',
    ]),
    ...mapState([
      'headers',
      'fileName',
      'targets',
      'mapSchema',
    ]),
  },
  methods:{
    async getDecision(only) {
      if (!this.target) {
        this.$message({
          type: 'warning',
          dangerouslyUseHTMString: true,
          message: (this.$i18n.t('page3.warning1'))
        });
        return;
      }
      this.showTarget = this.target.name;
      this.problem = this.$store.state.mapSchema[this.target.id].y.length;
      console.log("post file now.");
      let headers = [];
      let vue = this;
      //console.log(this.headers);
      this.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push(h.value));
      // csv导出法
      const tHeader = headers;
      const tableData = this.tData;
      const filename = this.fileName.split('.')[0];
      let className = this.mapSchema[this.target.id].y;
      //console.log(filename);
      let choose = [];
      if (only) {
        this.$store.state.historyLeft.forEach(e => {
          choose.push(e.name)
        })
        this.useFeather = choose.length;
      } else {
        this.useFeather = headers.length - 2;
      }
      this.$store.state.help = 'result';
      await mlAxios.post("getDecision", {
        "tHeader": tHeader,
        "tData": tableData,
        "filename": filename,
        "choose": choose,
        "target": this.target.name,
        "DownFile": true,
        "className": className,
        "language": this.language
      }, {timeout: 200000})
          .then(res => {
            console.log(res);
            vue.accuracy = res['data']['accuracy'];
            vue.precision = res['data']['precision'];
            vue.srcDecision = res['data']['src'];
            vue.MLmethod = 'Decision';
            vue.show = true;
          })
      vue.$emit('showDecision', vue.srcDecision);
    },
    async getKNN(only){
      if (! this.target){
        this.$message({
          type:'warning',
          dangerouslyUseHTMString:true,
          message:(this.$i18n.t('page3.warning1'))
        });
        return;
      }
      this.showTarget = this.target.name;
      this.problem = this.$store.state.mapSchema[this.target.id].y.length;
      console.log("post file now.");
      let headers = [];
      let vue = this;
      //console.log(this.headers);
      this.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push(h.value));
      // csv导出法
      const tHeader = headers;
      const tableData = this.tData;
      //console.log(filename);
      let className = this.mapSchema[this.target.id].y;
      let choose = [];
      if (only){
        this.$store.state.historyLeft.forEach(e => {choose.push(e.name)})
        this.useFeather = choose.length;
      }
      else{
        this.useFeather = headers.length - 2;
      }
      this.$store.state.help = 'result';
      await mlAxios.post("getKNN", {"tHeader":tHeader, "tData": tableData,  "choose":choose, "target": this.target.name, "className": className, "language": this.language}, {timeout: 200000})
          .then(res=>{
            console.log(res);
            vue.accuracy = res['data']['accuracy'];
            vue.precision = res['data']['precision'];
            vue.knnsrc = res['data']['src'];
            vue.MLmethod = 'KNN';
            vue.show = true;
          })
      vue.$emit('showKNN', vue.knnsrc);
    },

    async getCompare(only){
      this.show = false;
      if (! this.target){
        this.$message({
          type:'warning',
          dangerouslyUseHTMString:true,
          message:(this.$i18n.t('page3.warning1'))
        });
        return;
      }
      console.log("post file now.");
      let headers = [];
      let vue = this;
      //console.log(this.headers);
      this.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push(h.value));
      // csv导出法
      const tHeader = headers;
      const tableData = this.tData;
      let className = this.mapSchema[this.target.id].y;
      //console.log(filename);
      let choose = [];
      if (only){
        this.$store.state.historyLeft.forEach(e => {choose.push(e.name)})
      }
      this.$store.state.help = 'result';
      await mlAxios.post("getCompare", {"tHeader":tHeader, "tData": tableData,  "choose":choose, "target": this.target.name, "className": className,"language": this.language}, {timeout: 200000})
          .then(res=>{
            console.log(res);
            vue.Confusionsrc = res['data']['src1']
            vue.ROCsrc = res['data']['src2']
          })
      vue.$emit('showCompare', vue.Confusionsrc, vue.ROCsrc);
    },

    async getLogistic(only){
      if (! this.target){
        this.$message({
          type:'warning',
          dangerouslyUseHTMString:true,
          message:(this.$i18n.t('page3.warning1'))
        });
        return;
      }
      this.showTarget = this.target.name;
      this.problem = this.$store.state.mapSchema[this.target.id].y.length;
      console.log("post file now.");
      let headers = [];
      let vue = this;
      //console.log(this.headers);
      this.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push(h.value));
      // csv导出法
      const tHeader = headers;
      const tableData = this.tData;
      //console.log(filename);
      let className = this.mapSchema[this.target.id].y;
      let choose = [];
      if (only){
        this.$store.state.historyLeft.forEach(e => {choose.push(e.name)})
        this.useFeather = choose.length;
      }
      else{
        this.useFeather = headers.length - 2;
      }
      this.$store.state.help = 'result';
      await mlAxios.post("getLogistic", {"tHeader":tHeader, "tData": tableData,  "choose":choose, "target": this.target.name, "className": className,"language": this.language}, {timeout: 200000})
          .then(res=>{
            console.log(res);
            vue.accuracy = res['data']['accuracy'];
            vue.precision = res['data']['precision'];
            vue.logisticsrc = res['data']['src'];
            vue.MLmethod = 'Logistic';
            vue.show = true;
          })
      vue.$emit('showLogistic', vue.logisticsrc);
    },
    async getHeatMap(only) {
      if (!this.target) {
        this.$message({
          type: 'warning',
          dangerouslyUseHTMString: true,
          message: (this.$i18n.t('page3.warning1'))
        });
        return;
      }
      this.showTarget = this.target.name;
      console.log("post file now.");
      let headers = [];
      let vue = this;
      //console.log(this.headers);
      this.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push(h.value));
      // csv导出法
      const tHeader = headers;
      const tableData = this.tData;
      //console.log(filename);
      let choose = [];
      if (only) {
        this.$store.state.historyLeft.forEach(e => {
          choose.push(e.name)
        })
        choose.push(this.target.name)
      }
      this.$store.state.help = 'result';
      await mlAxios.post("getHeatmap", {
        "tHeader": tHeader,
        "tData": tableData,
        "choose": choose,
        "target": this.target.name
      }, {timeout: 200000})
          .then(res => {
            console.log(res);
            vue.heatmapsrc = res['data']['src'];
            vue.show=false;
          })
      vue.$emit('showHeatmap', vue.heatmapsrc);
    },
  },
  watch:{
    target() {
      this.$emit('getTarget', this.target.name);
    }
  }
}
</script>

<style scoped>

</style>