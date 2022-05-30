<template>
  <div>
    <div class="d-flex">
        <v-card elevation="4" shaped tile class="p-lg-2 m-2" style="width: 80%">
          <div class="d-flex">
            <div class="frame p-2 w-50">
              <draggable v-model="left" group="schema" animation="200" :emptyInsertThreshold="500" ghostClass="ghost" chosenClass="chosen" @change="onChange">
                <transition-group>
                  <v-chip class="item" v-for="(item, index) in left" :key="item.id"
                          :class="{sensitive:item.sensitive}"
                          close
                          @click:close="remove(index)"
                          @click="item.sensitive = ! item.sensitive; onChange();"
                  >{{item.name}}</v-chip>
                </transition-group>
              </draggable>
            </div>
            <v-btn class="ma-2" dark @click="moveAll">
              <v-icon dark left>mdi-arrow-left</v-icon>
              {{ $t('page4.button1') }}
            </v-btn>
            <div class="frame p-2 w-50">
              <v-chip class="item" v-for="(item, index) in right" :key="item.id" @click="move(index)">{{item.name}}</v-chip>
            </div>
          </div>
        </v-card>
        <v-card elevation="4" shaped tile class="p-lg-2 m-2" style="width: 20%">
          <v-card-title> {{$t('help.title')}} </v-card-title>
          <Guide :tip="tip"></Guide>
        </v-card>

    </div>
    <div>
      <v-card elevation="4" shaped tile :loading=false class="p-lg-2 m-2 w-100" style="height: fit-content">
      <v-card-title>{{this.fileName}}</v-card-title>
      <v-data-table :headers="downloadHeaders" :items="downloadData" :items-per-page="15" class="elevation-1" dense></v-data-table>
      <v-card-actions>
        <v-btn outlined rounded text @click="download">{{ $t('page4.button2') }}</v-btn>
      </v-card-actions>
    </v-card>
    </div>
  </div>
</template>

<script>
import {mapGetters, mapState} from "vuex";
import {mlAxios} from "../../plugins/machineLearning";
import draggable from "vuedraggable";
import Guide from "../Help/Guide"
export default {
  name: "DownloadFile",
  components: {
    draggable, Guide
  },
  created() {
    if (this.historyLeft.length !=0 ){
      this.left = this.historyLeft;
      this.right = this.historyRight;
    }
    else {
      this.left = [];
      let headers = this.$store.state.headers;
      // 不适合排序，字母序后，用户想看原csv发布后的隐私风险就很麻烦
      //headers = headers.sort(((a, b) =>a.text.localeCompare(b.text)));
      //console.log(headers);
      for (let i = 0; i < headers.length; i++) {
        this.right.push({
          id: i,
          name: headers[i].text,
          sensitive: false,
        })
      }
    }
    let headers = [];
    let vue = this;
    this.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push(h.value));
    const tHeader = headers;
    //console.log(this.left);
    const tableData = this.tData;
    let chooseHeader = [];
    this.downloadHeaders =[];
    //console.log('left:', this.left);
    this.left.forEach(h => {
      chooseHeader.push(h.name);
      this.downloadHeaders.push({'text': h.name, 'value': h.name})
    });
    //console.log('downloadHeaders:', this.downloadHeaders);
    if (tHeader.length != 0){
      mlAxios.post('PrintCSV', {"tHeader": tHeader, "tData": tableData, "chooseHeader": chooseHeader})
          .then(res => {
            //console.log(res);
            vue.downloadData = res['data']['tData'];
            //console.log('downloadData:', vue.downloadData)
          })
    }

  },
  data(){
    return{
      downloadHeaders:[],
      downloadData: [],
      left: [],
      right: [],
      tip: 'page4',
    }
  },
  computed: {
    mapType(){
      return this.$global.mapType
    },
    ...mapGetters([
      'headersName',
      'tData',
    ]),
    ...mapState([
      'headers',
      'fileName',
      'historyLeft',
      'historyRight',
    ]),
  },
  methods: {
    download() {
      let headers = [];
      this.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push(h.value));
      const tHeader = headers;
      //console.log(this.left);
      const tableData = this.tData;
      let chooseHeader = [];
      //console.log('left:', this.left);
      this.left.forEach(h => {
        chooseHeader.push(h.name);
      });
      const filename = this.fileName.split('.')[0];
      mlAxios.post("DownloadCSV",{'filename': filename, "tHeader": tHeader, "tData": tableData, "chooseHeader": chooseHeader},{responseType: "blob"})
          .then(res=>{
            const blob = new Blob([res.data]);
            const url = window.URL.createObjectURL(blob);
            const aLink = document.createElement("a");
            aLink.style.display = "none";
            aLink.href = url;
            aLink.setAttribute("download", filename+".csv");
            document.body.appendChild(aLink);
            aLink.click();
            document.body.removeChild(aLink); //下载完成移除元素
            window.URL.revokeObjectURL(url);
          })
      // todo 头疼，一直dic自动排序了
      // 可以直接从vue下载的方法只能舍弃了
      // CsvExportor.downloadCsv(tableData, {'header': tHeader}, "download.csv")

    },
    move(index){
      let obj = this.right[index]
      this.$delete(this.right, index)
      this.left.push(obj)
      this.onChange()
    },
    moveAll(){
      this.$set(this, 'left', this.left.concat(this.right))
      this.$set(this, 'right', [])
      this.onChange()
    },
    onChange(){
      let headers = [];
      let vue = this;
      this.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push(h.value));
      const tHeader = headers;
      //console.log(this.left);
      const tableData = this.tData;
      let chooseHeader = [];
      this.downloadHeaders =[];
      //console.log('left:', this.left);
      this.left.forEach(h => {
        chooseHeader.push(h.name);
        this.downloadHeaders.push({'text': h.name, 'value': h.name})
      });
      //console.log('downloadHeaders:', this.downloadHeaders);
      mlAxios.post('PrintCSV', {"tHeader": tHeader, "tData": tableData, "chooseHeader": chooseHeader})
          .then(res => {
            //console.log(res);
            vue.downloadData = res['data']['tData'];
            //console.log('downloadData:', vue.downloadData);
          })
    },
    remove(index){
      let obj = this.left[index]
      this.$delete(this.left, index)
      this.right.push(obj)
      this.right.sort((a,b) => a.id - b.id)
      this.onChange()
    },
  }
}
</script>

<style scoped>
.frame{
  /*background-color: rgb(246, 0, 0);*/
  border-style: solid;
  border-color: #848484;
  border-width: 1px;
  border-radius: 10px;
}
.chosen{
}
.ghost{
  background-color: pink !important;
}
.item{
  margin-left: 3px;
}
.sensitive{
  background-color: #868686 !important;
}
</style>