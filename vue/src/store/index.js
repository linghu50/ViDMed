import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        token: sessionStorage.getItem("token"),
        fileName: '',
        headers: [],
        sensitive: [],
        mapSchema: [],
        treeRoot: null, // webTree的root
        globalTreeRoot: null, //风险树的root
        schema: [],
        sensitives: [],
        filters: [],
        currentIndex: -1,
        history: [],
        operators: [],
        selectedRow: new Set(),
        historyLeft: [],   // 展示属性
        historyRight: [],  // 未被展示属性
        choose: [], // 被选中的下载对象
        targets: [], // 被选中的待预测对象
        help: 'upload', // 操作指南页面提示信息
        save: false,
    },
    mutations: {
        pushTData(state, tData) {
            // 删除currentIndex后length - currentIndex - 1个数据，即只保留到currentIndex（若currentIndex为-1即全部清空）
            // 然后再压入数据TData，并将currentIndex自增1
            state.history.splice(state.currentIndex + 1, state.history.length - state.currentIndex - 1)
            state.history.push(tData)
            state.currentIndex++;
            state.selectedRow.clear()
            console.log(state.history)
        },
        setToken(state, token){
            state.token = token
            sessionStorage.setItem("token", token)
        },
        setObj(state, newObj){
            state[newObj.type] = newObj.value
            //console.log('setObj', newObj.type)
        },
        selectedAdd(state, obj){
            if (Array.isArray(obj)) {
                obj.forEach(_obj=>state.selectedRow.add(_obj))
            } else {
                state.selectedRow.add(obj)
            }
            state.selectedRow = new Set(state.selectedRow)
        },
        selectedRemove(state, obj){
            if (Array.isArray(obj)) {
                obj.forEach(_obj=>state.selectedRow.delete(_obj))
            } else {
                state.selectedRow.delete(obj)
            }
            state.selectedRow = new Set(state.selectedRow)
        },
    },
    getters:{
        headersName(state){
            return state.headers.map(h=>h.text)
        },
        tData(state){
            return state.history[state.currentIndex] ? state.history[state.currentIndex].tData : undefined
        }
    },
})
