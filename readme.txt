语言上：1.datacube和springboot是java项目  2.vue是vue项目 3.math是python项目

建议使用IDEA+webstorm+pycharm

vue项目是前端项目，基于vue写的前端可视化内容。需要对npm和vue有一点点了解。（webstorm）

springboot是后端的服务器，基于Maven的spring的web服务器。 然后datacube我写的数据管理的的库，在IDEA中被springboot项目引用即可。后端运行springboot项目（其实就是Maven项目）

math是用来处理数据的，是一个Flask的web服务器，用来调用一些pyrhon上面的库。（python项目，也可以先不管它，目前有些功能没做完。所以我只是把接口接通了，实际上还没有过调用相关功能）

整个工作是前后端分离的，前端负责可视化（vue），后端负责数据管理（springboot）和数据处理（python）

java只需要maven方式打开springboot项目即可，datacube作为外链库（eclipse）或者moudle（IDEA）导入即可。

关于vue项目和maven项目的加载可能会涉及科学上网的问题。 很多库需要挂代理才能下下来


版本：
java：
jdk-15.0.2
org.apache.commons.math3 3.6.1

vue：
node环境 node 16.13.0 npm 8.1.0
npm install -g cnpm –registry=https://registry.npm.taobao.org
之后用cnpm代替npm，使用淘宝镜像
npm install 包名@版本号 如：npm install express@3.21.2
package.json依赖安装 


备注，npm有点问题，现在所有的工程直接用npm需要改权限
get-ExecutionPolicy 若为Restricted
则输入 Set-ExecutionPolicy -Scope CurrentUser 再输入RemoteSigned


后端sprintboot运行TPAApplication，关键在TpaController（基本操作都在这里，再函数跳转）
前端vue，直接run npm server，打开网页即可
datacube（数据结构管理）关键在operators的UpdataOP（增、删、改）和下面的TableCuboid（k、l、t）
python是一些数据处理，MAIN是仿真数据的加入（未完成）