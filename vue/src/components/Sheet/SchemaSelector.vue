<template>
  <div class="d-flex">
    <div class="frame p-2 w-50">
      <draggable v-model="left" group="schema" animation="200" :emptyInsertThreshold="500" ghostClass="ghost" chosenClass="chosen" @change="onChange">
        <transition-group>
          <v-chip class="item" v-for="(item, index) in left" :key="item.id"
                  :class="{sensitive:item.sensitive}"
                  close
                  @click:close="remove(index)"
                  @click="item.sensitive = ! item.sensitive; onChange();"
                  @contextmenu.prevent="targetAdd(item)"
          >{{item.name}}</v-chip>
        </transition-group>
      </draggable>
    </div>
    <div>
      <v-btn class="ma-2" dark @click="moveAll">
        <v-icon dark left>mdi-arrow-left</v-icon>
<!--        <font-awesome-icon :icon="['fas', 'long-arrow-left']" style="left: 5px"></font-awesome-icon>-->
        {{ $t('page2.button1') }}
      </v-btn>
      <v-btn class="ma-2" dark @click="saveLeft">
        {{ $t('page2.button2') }}
      </v-btn>
      <input type='text' v-model="targetFeature" @keyup.enter="selectPrimary" :placeholder="$t('page2.placeholder')" autofocus="autofocus" autocomplete="off"/>
      <v-btn class="ma-2" dark @click="selectPrimary">
        {{ $t('page2.button3') }}
      </v-btn>
      <br/>
      {{ $t('page2.button4') }}
      <br/>
      <div class="frame p-2" style="width: 380px">
        <v-chip class="item" v-for="(item,index) in this.targets"
                :key="index"
                close
                @click:close="targetDelete(index)"
        >{{item.name}}</v-chip>
      </div>
    </div>
    <div class="frame p-2 w-50">
      <v-chip class="item" v-for="(item, index) in right"
              :key="item.id"
              @click="move(index)"
              @contextmenu.prevent="targetAdd(item)"
      >{{item.name}}</v-chip>
    </div>

  </div>
</template>

<script>
import draggable from 'vuedraggable'
import {mapGetters, mapState} from "vuex";
import {mlAxios} from "../../plugins/machineLearning";

export default {
  components: {
    draggable,
  },
  created: function () {
    //console.log('new');
    if (this.save) {
      this.left = this.historyLeft;
      this.right = this.historyRight;
      this.onChange();
      this.$store.state.save = false;
    } else {
      if (this.$store.state.help === 'operation' || this.$store.state.help === 'result')
        this.$store.state.help = 'page2';
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
    this.targets.forEach(h => this.targetNames.push(h.name))
  },
  data() {
    return {
      left:[],
      right:[],
      targetFeature: null,
      targetNames: [],  // 用于防止多次添加
    };
  },
  computed: {
    ...mapGetters([
       'headersName',
       'tData',
     ]),
    ...mapState([
      'fileName',
      'historyLeft',
      'historyRight',
      'save',
      'targets',
    ]),
  },
  methods: {
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
      let sensitive = []
      this.left.forEach(d=>d.sensitive && sensitive.push(d.id))
      // 触发外组件的change函数，并将后两个作为参数传出
      this.$emit('change', this.left.map(d=>d.id), this.right.map(d=>d.id), sensitive)
      let lleft = this.left
      let rright = this.right
      this.$store.state.historyRight = rright
      this.$store.state.historyLeft = lleft
      this.$store.state.help = 'operation'
      //console.log('left:', this.left);
      //console.log(this.$store.state.right)
    },
    targetAdd(item){
      if (!this.targetNames.includes(item.name)){
        this.targets.push({'name':item.name, 'id': item.id});
        this.targetNames.push(item.name)
        //console.log(this.targets)
      }
    },
    targetDelete(index){
      console.log('delete', index);
      this.$delete(this.targets, index);
      this.$delete(this.targetNames, index);
    },
    deleteByName(targetList, key, value, result){
      targetList.forEach(function (item, index, arr){
        if (item[key] == value){
          let target = window.deepCopy(item);
          console.log('target', target);
          arr.splice(index, 1);
          result.push(target);
        }
      })
    },
    saveLeft(){
      this.$store.state.save = true;
    },
    selectPrimary(){
      if (this.targetFeature == null){
        this.$message({
          type:'warning',
          dangerouslyUseHTMString:true,
          message:(this.$i18n.t('page2.warning2'))
        });
        return;
      }
      console.log("get primary now.");
      let headers = [];
      let vue = this;
      //console.log(this.headers);
      this.$store.state.headers.forEach(h => (h.type === 0 || h.type === 1) && headers.push(h.value));
      // csv导出法
      const tHeader = headers;
      const tableData = this.tData;
      const feather = this.targetFeature;
      console.log(this.targetFeature);
      if (headers.indexOf(feather)==-1){
        this.$message({
          type:'warning',
          dangerouslyUseHTMString:true,
          message:(this.$i18n.t('page2.warning1') + feather)
        });
        return;
      }
      // 及时复原
      this.right = [];
      for (let i = 0; i < headers.length; i++) {
        this.right.push({
          id: i,
          name: headers[i],
          sensitive: false,
        })
      }
      this.left = [];
      mlAxios.post("getPrimary", {"tHeader":tHeader, "tData": tableData, "feather": feather})
          .then(res=>{
            console.log(res);
            let primary = res['data']['primary'];
            let result = [];

            primary.forEach(p => {
              vue.deleteByName(this.right, 'name', p, result);
            })
            result.forEach(r => {
              vue.left.push(r);
            })
            vue.onChange();
          })
    },
    remove(index){
      let obj = this.left[index]
      this.$delete(this.left, index)
      this.right.push(obj)
      this.right.sort((a,b) => a.id - b.id)
      this.onChange()
    },
  },
  name: "SchemaSelector"
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