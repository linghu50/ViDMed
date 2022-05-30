<template>
  <div class="d-flex">
    <div class="col p-0" style="width: 20%">
      <v-card elevation="4" shaped tile class="p-lg-2 m-2" style="width: 400px" :disabled="loading">
        <v-card-title>{{$t('page1.cardTitle1')}}</v-card-title>
        <div>
          <!--    点击文件上传位置后触发      -->
          <v-file-input @change="onAddFiles" counter accept=".csv" truncate-length="15" class="w-75 d-lg-inline-flex m-2"></v-file-input>
        </div>
      </v-card>
      <!--   由loaded函数的返回结果，即headers.length决定是否显示接下来内容   -->
      <v-card v-if="loaded" elevation="4" shaped tile class="p-lg-2 m-2" style="width: 400px">
        <v-list  dense style="height: 500px" class="overflow-auto">
          <v-select :items="[0,1,2,3]" v-for="(header, index) in this.headers" :key="index" :label="header.text" v-model="header.type" >
            <!--    选中的数据类型      -->
            <template v-slot:selection="{item}">
              <span>{{$t('page1.mapType')[item]}}</span>
            </template>
            <!--    下拉框中可选的数据类型      -->
            <template v-slot:item="{item}">
              {{$t('page1.mapType')[item]}}
            </template>
          </v-select>
        </v-list>
        <v-card-actions>
          <v-btn outlined rounded text @click="submit">{{$t('page1.button1')}}</v-btn>
        </v-card-actions>
      </v-card>
    </div>
    <!--:loading是加载状态，根据loading的值，False表示还在加载-->
    <div style="width: 80%">
      <v-card elevation="4" shaped tile :loading="loading" class="p-lg-2 m-2 w-80" style="height: fit-content">
        <v-card-title>{{this.fileName}}</v-card-title>
        <v-data-table :headers="this.headers" :items="this.tData" :items-per-page="15" class="elevation-1" dense></v-data-table>
      </v-card>
      <v-card elevation="4" shaped tile class="p-lg-2 m-2 w-80" style="height: fit-content">
        <v-card-title> {{$t('help.title')}} </v-card-title>
        <Guide :tip='tip'> </Guide>
      </v-card>

    </div>
  </div>
</template>

<script>
import xlsx from 'xlsx'
import {mapState, mapMutations, mapGetters} from 'vuex'
import Guide from '../Help/Guide'
import {mlAxios} from "../../plugins/machineLearning";
export default {
  name: "UploadFile",
  components: {Guide},
  data(){
    return{
      file: null,
      loading: false,
      tip: 'page1',
      accuracy: null,
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
    ]),
  },
  methods: {
    async submit() {
      let Stime = (new Date()).getTime();
      this.$store.state.targets = [];
      this.$store.state.historyLeft = [];
      this.$store.state.historyRight = [];
      let headers = []
      this.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push({
        // value: key,
        // type: Number.isFinite(data[0][key]) ? 0:1,
        name: h.value,
        type: h.type
      }))
      let data = {
        headers,
        desserts: this.tData,
      }
      if (this.headers.length > 0) {
        this.$store.state.help = 'page2';
        let _this = this;
        await this.$http.post('uploadExcel', data).then(res => {
          if (res.data.code === 200) {
            let mapSchema = res.data.data.mapSchema;
            _this.setToken(res.data.data.token);
            _this.setObj({type: 'mapSchema', value: mapSchema})
            let filter = []
            let index = 0;
            for (let map of mapSchema) {
              let type = _this.headers[index++].type
              if (type === 1) {
                filter.push([...map.y])
              } else if (type === 0) {
                filter.push([[map.y[0].min, map.y[0].max]])
              }
            }
            _this.setObj({type: 'filters', value: filter})
            }
        })
        let cerSchema = [];
        // 起始的风险用全风险
        for (let i = 0; i < headers.length; i++) {
          cerSchema.push(i);
        }
        await this.getCer(cerSchema);
        let Etime = (new Date()).getTime()-Stime;
        console.log('upload submit time:', Etime);
      } else {
        this.$message({
          type: 'warning',
          dangerouslyUseHTMString: true,
          message: (this.$i18n.t('page1.warning1'))
        });
      }
    },
    getCer(cerSchema) {
      let data = {
        schema: cerSchema,
      }
      let vue = this;
      this.$http.post('privacyAssess', data).then(res => {
        if (res.data.code === 200) {
          vue.$store.state.history[0].risk = res.data.data;
        }
      })
    },
    onAddFiles(file){
      let Stime = (new Date()).getTime();
      //console.log(Stime);
      this.file = file
      if (!this.file) return;
      const reader = new FileReader();
      let vue = this
      this.loading = true
      // 要改为同步请求，使用async和wait，不然的话，没得到accuracy就加入history了
      reader.onload = async function (e) {
        const result = e.target.result;
        const workbook = xlsx.read(result, {type: 'binary'});
        let data = xlsx.utils.sheet_to_json(workbook.Sheets[workbook.SheetNames[0]])
        vue.headers.length = 0
        let max_index = data.length;
        let delete_len = [];
        //console.log(max_index);
        //console.log(data[0]); // 测试
        // data[0]是第一行数据，内容是字典形式，key是属性名(Excel[0,j])，value是值(Excel[1,j])
        Object.keys(data[0]).forEach(key => {
          let na_count = 0;
          for (let i = 0; i < max_index; i++) {
            if (data[i][key] == 'NA') na_count++;
          }
          if (na_count > max_index * 0.5) {
            // 如果一半以上为NA则警告且舍弃；仅仅只是在headers中舍弃了，但在tData中仍会传递
            // 不过没有关系，在后台处理数据插入datacube前数据需要转化为TabularDataPoint，此时是根据headers的值读的数据，经测试确实可以删除
            // 特别注意，此时this已经不是外面的this了，而是一个新的this，所以不能用this，只能用vue
            delete_len.push(key);
            return;
          }
          let index = 0;
          // 顺延直到有一个非NA值来判断属性类型
          while (data[index][key] == 'NA') {
            index++;
          }
          let key_type = 0;
          if (Number.isInteger(data[index][key])){
            if (data[index][key] < 20){
              key_type = 1;
            }
          }
          //let key_type = 1//Number.isFinite(data[index][key]) ? 0:1
          vue.headers.push({
            text: key,
            value: key,
            type: key_type,
          })
          //console.log("data["+index+"]["+key+"]"+data[index][key]); // 测试
          for (let datum of data) {
            datum["_" + key] = datum[key]
          }
        })
        if (delete_len.length) {
          vue.$message({
            type: 'warning',
            dangerouslyUseHTMString: true,
            message: (delete_len.toString() + vue.$i18n.t('page1.warning2'))
          });
          console.log(delete_len);
        }
        for (let i = 0; i < data.length; i++) {
          data[i]['_index'] = i;
        }
        // 将state的currentIndex属性置为-1
        vue.setObj({type: 'currentIndex', value: -1})
        //console.log('data', data)

        // 开始评估
        let headers = [];
        //console.log(this.headers);
        vue.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push(h.value));
        // csv导出法
        const tHeader = headers;
        const tableData = data;
        const filename = vue.fileName.split('.')[0];
        let key = Object.keys(data[0])[Object.keys(data[0]).length/2 - 1];
        let class_name = []
        for (let i = 0; i < max_index; i++) {
          if (!class_name.includes(data[i][key])) class_name.push(data[i][key])
        }
        console.log(class_name)
        await vue.getAccuracy({
          "tHeader": tHeader,
          "tData": tableData,
          "filename": filename,
          "choose": [],
          "DownFile": false,
          "target": tHeader[tHeader.length - 1],
          "className": class_name,
          "language": vue.$i18n.locale
        });
        //console.log('continue', vue.accuracy);
        // 老是忘记，函数里面不能再用this
        vue.pushTData({action: ["Base", "upload"], accuracy: vue.accuracy, tData: data, risk: null})

        vue.setObj({type: 'fileName', value: vue.file.name})
        vue.name = name
        vue.loading = false
        let Etime =(new Date()).getTime()-Stime;
        console.log('upload show time:',Etime);
      };
      reader.readAsBinaryString(this.file);
      this.$store.state.help = 'submit';
    },
    getAccuracy(data){
      console.log(data)
      let vue = this;
      return new Promise((resolve,reject) => {
        mlAxios.post("getDecision", data, {timeout: 200000})
            .then(res => {
              //console.log(res);
              vue.accuracy = res['data']['accuracy'];
              console.log('await',vue.accuracy)
              resolve(res)
            }).catch(err => reject(err))
      })
    },

    ...mapMutations([
        'setObj',
        'pushTData',
        'setToken'
    ]),
  }
}
</script>

<style scoped>

</style>