<template>
  <div>
    {{ $t('page3.description2') }}
    <v-card-actions style="height:fit-content;width: fit-content">
      <v-btn outlined rounded text @click="showTree()">{{ $t('page3.button14') }}</v-btn>
    </v-card-actions>
    <v-card-actions style="height:fit-content;width: fit-content">
      <v-btn outlined rounded text @click="getFile()">{{ $t('page3.button13') }}</v-btn>
    </v-card-actions>
    <div class="pdf" v-show="fileType === 'pdf'" v-if="show">
<!--      <p class="arrow">-->
<!--        // 上一页-->
<!--        <span @click="changePdfPage(0)" class="turn" :class="{grey: currentPage==1}">Preview</span>-->
<!--        {{currentPage}} / {{pageCount}}-->
<!--        // 下一页-->
<!--        <span @click="changePdfPage(1)" class="turn" :class="{grey: currentPage==pageCount}">Next</span>-->
<!--      </p>-->
<!--      // 自己引入就可以使用,这里我的需求是做了分页功能,如果不需要分页功能,只要src就可以了-->
      <pdf
          :src="src"
          :page="currentPage"
          @num-pages="pageCount=$event"
          @page-loaded="currentPage=$event"
          @loaded="loadPdfHandler">
      </pdf>
    </div>
  </div>
</template>

<script>
import pdf from 'vue-pdf'
import {mlAxios} from "../../plugins/machineLearning";
import {mapState} from "vuex";
export default {
  name: "ShowDecisionTree",
  components: {pdf},
  data(){
    return{
      test: 'test',
      show: false,
      currentPage: 0, // pdf文件页码
      pageCount: 0, // pdf文件总页数
      fileType: 'pdf', // 文件类型
      src: '', // pdf文件地址
    }
  },
  computed: {
    ...mapState([
      'fileName',
    ]),
  },
  props:{
    target: String,
  },
  methods: {
    showTree() {
      this.show = true;
      console.log("show tree-pdf now.");
      const filename = this.fileName.split('.')[0];
      let vue = this;
      mlAxios.post("DownloadPDF",{'filename': filename, 'target': vue.target},{responseType: "blob"})
          .then(res=> {
            this.pdfUrl = window.URL.createObjectURL(new Blob([res.data], {type: 'application/pdf'}));
            this.src = this.pdfUrl;
            this.src = pdf.createLoadingTask(this.src);
          })
    },
    getFile(){
      console.log("download tree-pdf now.");
      const filename = this.fileName.split('.')[0];
      let vue = this;
      mlAxios.post("DownloadPDF",{'filename': filename, 'target': vue.target},{responseType: "blob"})
          .then(res=>{
            const blob = new Blob([res.data]);
            const url = window.URL.createObjectURL(blob);
            const aLink = document.createElement("a");
            aLink.style.display = "none";
            aLink.href = url;
            aLink.setAttribute("download", filename+".pdf");
            document.body.appendChild(aLink);
            aLink.click();
            document.body.removeChild(aLink); //下载完成移除元素
            window.URL.revokeObjectURL(url);
          })
    },
    // 改变PDF页码,val传过来区分上一页下一页的值,0上一页,1下一页
    // changePdfPage(val){
    //   // console.log(val)
    //   if (val === 0 && this.currentPage > 1) {
    //     this.currentPage--
    //     // console.log(this.currentPage)
    //   }
    //   if (val === 1 && this.currentPage < this.pageCount) {
    //     this.currentPage++
    //     // console.log(this.currentPage)
    //   }
    // },

    // pdf加载时
    loadPdfHandler() {
      this.currentPage = 1 // 加载的时候先加载第一页
    },
  },
}
</script>

<style scoped>

</style>