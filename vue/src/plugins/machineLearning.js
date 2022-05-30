import axios from 'axios'

// 关于python的重定向在vue.config.js文件中
let mlAxios = axios.create({
    baseURL: '/python',
    timeout: 30000,
    headers: {
        'content-type': 'application/x-www-form-urlencoded'
    },
    withCredentials:true
});


function testHello(){
    return "hello";
}


export {testHello, mlAxios}