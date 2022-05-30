import Vue from 'vue'
import VueI18n from 'vue-i18n'
Vue.use(VueI18n )
import zh from './zh.js'
import en from './en.js'

export default new VueI18n({
    locale : localStorage.getItem('lang') || 'zh', // 从locale属性获得语言
    messages: {  // 文案
        zh, // 文案的中文版
        en // 文案的英文版
    }
})

