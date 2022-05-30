<template>
  <div class="d-flex">
    <div class="col-9 p-0">
      <v-card elevation="4" shaped tile class="p-lg-2 m-2 w-100" style="height: 850px">
        <SchemaSelector @change="requestBasicTree"></SchemaSelector>
        <div class="d-flex pl-1 overflow-x-auto">
          <AttributeHeader class="p-2" v-for="(s) in schema" :key="s" :s="s"></AttributeHeader>
        </div>

        <div class="overflow-auto" v-if="overView" style="height:600px">
          <OverviewDataRow v-for="(item) in itemsList" :key="item.originData"
                           :r-data="tData[item.originData]"
                           :schema="schema"
                           :path="item.path"
                           :agg-start="item.aggStart"
                           :agg-end="item.aggEnd">
          </OverviewDataRow>
        </div>
        <v-virtual-scroll
            v-else
            height="600"
            item-height="22"
            :items="itemsList"
            @contextmenu="contextmenu"
        >
          <template v-slot:default="{item}">
            <SDataRow
                v-if="!item.isAgg"
                :agg-end="item.aggEnd"
                :agg-start="item.aggStart"
                :path="item.path"
                :r-data="tData[item.originData]"
                :schema="schema"
                @aggClick="aggClick($event, item)"
            ></SDataRow>
            <!--  html中是-命名，内部的js是驼峰命名法  -->
            <SDataGroupRow
                v-else
                :schema="schema"
                :path="item.path"
                :agg-start="item.aggStart"
                :agg-end="item.aggEnd"
                :r-data-group="rDataGroup(item.originData)"
                @aggClick="aggClick($event, item)"
                @mergeGroup="mergeGroup"
            ></SDataGroupRow>
          </template>
        </v-virtual-scroll>
        <v-menu
            v-model="showMenu"
            :position-x="menuX"
            :position-y="menuY"
            absolute
            offset-y
        >

          <v-list flat>
            <v-list-item>
              <DPNoiseSetting :cerSchema="cerSchema"></DPNoiseSetting>
              <!--              <v-list-item-content>add dp noise</v-list-item-content>-->
            </v-list-item>

            <v-list-item>
              <font-awesome-icon :icon="['fas', 'times']" style="color:red;"></font-awesome-icon>
              <v-list-item-content>{{ $t('dp.menu2') }}</v-list-item-content>
            </v-list-item>

          </v-list>
        </v-menu>
      </v-card>
    </div>
    <div class="col-4 pt-0 pr-0">
      <v-card elevation="4" shaped tile class="p-lg-2 m-2" style="width: 73%">
        <v-switch v-model="overView" :label="$t('page2.label')"></v-switch>
      </v-card>
      <v-card elevation="4" shaped tile class="p-lg-2 m-2" style="width: 73%">
        <!--   在这里传递了tree-root参数，是webtree的根     -->
        <GlobalTree :tree-root="globalTreeRoot" :cer="cer"  @changeID="highlightTree" @quickMerge="quickMerge"></GlobalTree>
      </v-card>
      <v-card elevation="4" shaped tile class="p-lg-2 m-2" style="width: 73%">
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
      <v-card elevation="4" shaped tile class="p-lg-2 m-2" style="width: 73%">
        <v-card-title> {{$t('help.title')}} </v-card-title>
        <Guide :tip="tip"> </Guide>
      </v-card>
    </div>
  </div>
</template>

<script>
import {mapGetters, mapMutations, mapState} from 'vuex'
import AttributeHeader from "./AttributeHeader";
import SchemaSelector from "./SchemaSelector";
import GlobalTree from "./GlobalTree/GlobalTree";
import SDataRow from "./Row/SDataRow";
import SDataGroupRow from "./Row/SDataGroupRow";
import * as mathUtils from "../../plugins/mathUtils";
import DPNoiseSetting from "./Dialog/DPNoiseSetting";
import OverviewDataRow from "./Row/OverviewDataRow";
import Guide from "../Help/Guide"
import {mlAxios} from "../../plugins/machineLearning";
export default {
  name: "SheetPage",
  components: {OverviewDataRow, DPNoiseSetting, SDataGroupRow, SDataRow, GlobalTree, SchemaSelector, AttributeHeader, Guide},
  data() {
    return {
      selectedItem: 1,
      width: 180,
      itemsList: [],
      showMenu: false,
      overView: false,
      menuX: 0,
      menuY: 0,
      highlightID: null,
      tip: 'page2',
      accuracy: null,
      cer: null, // 风险量化值
      cerSchema: [],
    }
  },
  computed: {
    ...mapState([
      'treeRoot',
      'globalTreeRoot',
      'schema',
      'sensitives',
      'headers',
      'mapSchema',
      'filters',
      'currentIndex',
      'history',
    ]),
    ...mapGetters([
      'tData',
      'headersName'
    ]),
  },
  methods: {
    ...mapMutations([
      'pushTData',
    ]),
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
        _this.getCer();
        // _this.setObj({type:'treeRoot', value:res.data.data})
      })
    },
    contextmenu(e) {
      e.preventDefault()
      this.showMenu = false
      this.menuX = e.clientX
      this.menuY = e.clientY
      this.$nextTick(() => {
        this.showMenu = true
      })
    },
    rDataGroup(group) {
      let _this = this;
      return (function dfs(list, root) {
        root.forEach(item => {
          if (item.isAgg) {
            dfs(list, item.originData)
          } else {
            list.push(_this.tData[item.originData])
          }
        })
        return list
      })([], group)
    },
    findNodeByPath(path, root){
      for (let i = 0; i < path.length; i++) {
        root = root.children.find(child=>child.labels.equal(path[i]))
        if(!root) return
      }
      return root;
    },
    async mergeGroup(path1, path2){
      console.log('truepath:', path1);
      // op需要将modify构造好，后端只执行
      // tDataList中存储需要合并数据的index
      const tDataList = [...this.findNodeByPath(path1, this.treeRoot).content.d, ...this.findNodeByPath(path2, this.treeRoot).content.d]
      const set = new Set()
      path1[path1.length - 1].forEach(l=>set.add(l))  // 将路径1待合并项的标签加入set中
      path2[path2.length - 1].forEach(l=>set.add(l))
      const ms = this.mapSchema[this.schema[path1.length - 1]].y  // 合并操作针对的属性的属性标签列表
      const label = []
      for (let d of set) {
        label.push(ms[d])     // 标签合并，原先path1是1,2，path2是3，则合并后label是1,2,3
      }
      const value = this.headers[this.schema[path1.length - 1]].value   // 合并项的属性名
      // todo 弄清楚modify存储了什么
      const modify = {}
      let newTData = [...this.tData]
      // TDataList存储的是待合并数据的index
      for (let i of tDataList) {
        //console.log('i', i)
        let newRow = window.deepCopy(this.tData[i])   // 不修改TData的前提下修改newTData
        newTData[newRow['_index']] = newRow
        newRow[value] = label
        let clean = {}
        for (let header of this.headers) {
          clean[header.value] = newRow[header.value]  // 将修改后的数据放入modify中，对应key为index
        }
        modify[i] = clean
      }
      // 开始评估效用
      let headers = [];
      let _this = this;
      //console.log(this.headers);
      this.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push(h.value));
      const tHeader = headers;
      const tableData = newTData;
      const filename = null;
      let choose = [];
      this.$store.state.historyLeft.forEach(e => {choose.push(e.name)})
      await this.getAccuracy({"tHeader":tHeader, "tData": tableData, "filename": filename, "choose":choose, "target": tHeader[tHeader.length - 1], "DownFile":false, "className": _this.mapSchema[_this.mapSchema.length -1].y, "language": this.$i18n.locale});

      await this.$http.post('updateTableau', {
        modify
      }).then(res => {
          _this.itemsList.length = 0
          _this.setObj({type:'treeRoot', value:_this.handleList(_this.itemsList, res.data.data, [])})
          _this.setObj({type:'globalTreeRoot', value: res.data.data})
        // _this.setObj({type:'treeRoot', value:res.data.data})
      })
      await this.getCer();
      this.pushTData({action:["Merge", "merge"], tData:newTData, accuracy: this.accuracy, risk: this.cer})
    },
    async mergeList(rootPath, pathlist) {
      console.log("merge", pathlist);
      let tDataList = []
      const set = new Set()
      for (let onePath of pathlist) {
        //console.log('onePath', onePath);
        // tDataList是一个一维数组，不能直接push，要每个元素都push进去
        this.findNodeByPath(onePath, this.treeRoot).content.d.forEach(l => tDataList.push(l));
        //tDataList.push(this.findNodeByPath(onePath, this.treeRoot).content.d)
        onePath[onePath.length - 1].forEach(l => set.add(l))  // 将路径1待合并项的标签加入set中
      }
      //console.log('set', set);
      const ms = this.mapSchema[this.schema[rootPath.length]].y  // 合并操作针对的属性的属性标签列表
      const label = []
      for (let d of set) {
        label.push(ms[d])     // 标签合并，原先path1是1,2，path2是3，则合并后label是1,2,3
      }
      //console.log('label', label);
      const value = this.headers[this.schema[rootPath.length]].value   // 合并项的属性名
      //console.log('value', value);
      const modify = {}
      let newTData = [...this.tData]
      // TDataList存储的是待合并数据的index
      for (let i of tDataList) {
        //console.log('i', i)
        let newRow = window.deepCopy(this.tData[i])   // 不修改TData的前提下修改newTData
        //console.log('newRow', newRow);
        newTData[newRow['_index']] = newRow
        newRow[value] = label
        let clean = {}
        for (let header of this.headers) {
          clean[header.value] = newRow[header.value]  // 将修改后的数据放入modify中，对应key为index
        }
        modify[i] = clean
      }

      // 开始评估效用
      let headers = [];
      let _this = this;
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


      await this.$http.post('updateTableau', {
        modify
      }).then(res => {
        _this.itemsList.length = 0
        _this.setObj({type: 'treeRoot', value: _this.handleList(_this.itemsList, res.data.data, [])})
        _this.setObj({type: 'globalTreeRoot', value: res.data.data})

        // _this.setObj({type:'treeRoot', value:res.data.data})
      })
      await this.getCer();
      this.pushTData({action: ["Merge", "merge"], tData: newTData, accuracy:this.accuracy, risk: this.cer})
      //console.log(this.treeRoot);
    },
    quickMerge(data){
      console.log('Merge for ', data.pathID)
      let labelTags = data.pathID.split('-');
      //console.log(labelTags);
      let rootPath = [];
      labelTags.forEach(tag => {
        if (tag != 'A'){
          let label = [];
          tag.split(',').forEach(h => {
            label.push(Number(h));
          })
          rootPath.push(label);
        }
      })
      console.log('path', rootPath);
      let node = this.findNodeByPath(rootPath,this.treeRoot);
      let pathlist = [];
      //console.log(data.threshold);
      console.log(node);
      for (let child of node.children){
        console.log('k', child.content.k);
        if (child.content.k < data.threshold){
          //console.log('child', child);
          let onePath = window.deepCopy(rootPath);
          onePath.push(child.labels);
          pathlist.push(onePath);
        }
      }
      if (pathlist.length > 0) {
        if (pathlist.length ==1 ) {
          // 子节点只有一个有风险，向满足阈值的低者合并
          let kMin = 10000;
          let addLabel = null;
          for (let child of node.children) {
            //console.log(child.content.k);
            if (child.content.k < kMin && child.content.k>=data.threshold) {
              addLabel = child.labels
            }
          }
          if (addLabel){
            // 子节点除了不满足阈值的结点外还有，则向满足阈值的低者合并
            let onePath = window.deepCopy(rootPath);
            onePath.push(addLabel);
            pathlist.push(onePath);
            this.mergeList(rootPath, pathlist);
          }
          else{
            // 子节点只有不满足阈值的一个结点，无法操作
            console.log('need to merge but no way.');
            this.$message({
              type:'warning',
              dangerouslyUseHTMString:true,
              message:(this.$i18n.t('page2.warning3'))
            });
          }
        }
        else {
          // 子节点有两个及以上的不满足阈值的结点，相互合并即可
          console.log('need to merge and done.')
          this.mergeList(rootPath, pathlist);
        }
      }
      else{
        console.log('need no merge.')
      }
    },
    aggClick(index, item){
      let s=0,e=0;
      for (s = this.itemsList.indexOf(item); s >= 0; s--) {
        if(this.itemsList[s].aggStart.has(index)) {
          break
        }
      }
      for (e = this.itemsList.indexOf(item); e < this.itemsList.length; e++) {
        if(this.itemsList[e].aggEnd.has(index)) {
          break
        }
      }
      if(!item.isAgg || index < item.path.length - 1) {
        const groupItem = {
          isAgg: true,
          originData: null,
          aggStart: null,
          aggEnd: null,
          path: null,
        }
        groupItem.originData = this.itemsList.splice(s, e - s + 1, groupItem)
        groupItem.aggStart = new Set(groupItem.originData[0].aggStart)
        groupItem.aggEnd = new Set(groupItem.originData[e - s].aggEnd)
        groupItem.path = groupItem.originData[0].path.slice(0, index + 1)
        this.findNodeByPath(groupItem.path, this.treeRoot).collapse = true;
      } else {
        this.itemsList.splice(s, e - s + 1, ...item.originData)
        this.findNodeByPath(this.treeRoot, item.path).collapse = false;
      }

    },
    getCer() {
      let data = {
        schema: this.cerSchema,
      }
      let vue = this;
      this.$http.post('privacyAssess', data).then(res => {
        if (res.data.code === 200) {
          vue.cer = res.data.data;
        }
      })
    },
    async requestBasicTree(leftSchema, rightSchema, sensitives) {
      let data = {
        schema: leftSchema,
        sensitives: sensitives
      }
      let _this = this;
      //console.log(leftSchema);
      //console.log(sensitives);
      await this.$http.post('updateSchema', data).then(res => {
        _this.setObj({type: 'schema', value: leftSchema})
        _this.setObj({type: 'sensitives', value: sensitives})

        _this.itemsList.length = 0;
        _this.setObj({type: 'treeRoot', value: _this.handleList(_this.itemsList, res.data.data, [])})
        _this.setObj({type: 'globalTreeRoot', value: res.data.data})
      })
      this.cerSchema = [];
      leftSchema.forEach(d => {
        this.cerSchema.push(d)
      });
      if (this.cerSchema.length < 10) {
        let count = 0;
        for (let i = this.cerSchema.length; i < 10 && count < rightSchema.length; i++) {
          this.cerSchema.push(rightSchema[count]);
          count = count + 1
        }
      }
      await this.getCer();
    },
    highlightTree(data){
      // highlightTree会一直到当前标红的上一级都是同标签，所以要调整的时候直接在本级圆环调整
      // 后台处理时对于前k-1个标签只查找对应的，对于第k个标签查全
      this.highlightID = data.highlightID
      //console.log('highlightID:', this.highlightID)
      let vue = this;
      let labelTags = this.highlightID.split('-');
      //console.log(labelTags);
      let labels = [];
      labelTags.forEach(tag => {
        if (tag != 'A'){
          let label = [];
          tag.split(',').forEach(h => {
            label.push(Number(h));
          })
          labels.push(label);
        }
      })
      for (let i=labels.length; i<this.schema.length; i++){
        labels.push([]);
      }
      console.log(labels);
      //console.log(this.schema);
      let highlightData = {
        schema: this.schema,
        sensitives: this.sensitives,
        labels: labels,
      }
      //this.$store.state.save = true;
      this.$http.post('highlightSchema', highlightData).then(res => {
        //vue.set.itemsList.length = 0;
        vue.itemsList.length = 0;
        vue.setObj({type:'treeRoot', value: vue.handleList(vue.itemsList, res.data.data, [])});
      })

    },
    handleList(list, root, path) {
      if(!root) return list
      let start = list.length
      let _this = this
      if (root.children.length > 0) {
        root.children.forEach(child => {
          let s = _this.schema[path.length]
          let f = _this.filters[s]
          let found = false
          if (_this.headers[s].type === 0) {
            found = true;
          } else {
            for (let label of child.labels) {
              if (f.indexOf(_this.mapSchema[s].y[label]) >= 0) {
                found = true
                break
              }
            }
          }
          if (found) {
            path.push(child.labels)
            this.handleList(list, child, path)
            path.pop()
          }
        })
      } else {
        root.content.d.forEach(index => {
          let pass = true
          for (let s of _this.schema) {
            if (_this.headers[s].type == 0) {
              let value = _this.tData[index][_this.headers[s].value]
              let f = _this.filters[s][0]
              if (value < f[0] || value > f[1]) {
                pass = false;
                break;
              }
            }
          }

          if (pass) {
            list.push({
              isAgg: false,
              aggStart: new Set(),
              aggEnd: new Set(),
              originData: index,
              path: [...path],
            })
          }
        })
      }
      let end = list.length - 1
      if (end >= start) {
        list[start].aggStart.add(path.length - 1)
        list[end].aggEnd.add(path.length - 1)
      }
      return root
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
    ...mapMutations([
      'setObj',
    ]),
  },
  watch: {
    filters(){
      console.log('update')
      mathUtils.distributionN([1, 2, 3], [1, 2, 3]).then(res=>{
        console.log(res);
      })
      this.itemsList.length = 0;
      this.handleList(this.itemsList, this.treeRoot, [])
    },
  },
  created() {
  },
  mounted() {
    this.itemsList.length = 0;
    this.handleList(this.itemsList, this.treeRoot, [])
  }
}
</script>

<style scoped>

</style>