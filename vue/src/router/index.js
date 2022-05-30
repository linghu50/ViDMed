import Vue from 'vue'
import VueRouter from 'vue-router'
import Introduce from "../components/Help/Introduce";
import UploadFile from "../components/Page1/UploadFile";
import SheetPage from "../components/Sheet/SheetPage";
import UtilityAnalysis from "../components/Utility/UtilityAnalysis";
import DownloadFile from "../components/Download/DownloadFile";

Vue.use(VueRouter)

export default new VueRouter({
    routes: [
        { path: '/', redirect: '/introduce' },
        { path: '/introduce', name:'introduce', component: Introduce},
        { path: '/privacy', name:'sheet', component: SheetPage},
        { path: '/upload', name:'upload', component: UploadFile },
        { path: '/utility', name:'utility', component: UtilityAnalysis },
        { path: '/release', name:'download', component: DownloadFile },
    ],
})
