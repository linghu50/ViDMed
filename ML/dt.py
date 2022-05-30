#!/usr/bin/env python
# -*- coding: utf-8 -*-

#导入需要的算法库和模块
from sklearn import tree
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
#wine = load_wine()
#print(len(wine.data))
#print(wine.data[0])
# print(wine.data.shape)
# print(wine.target)
# print(wine.target.shape)
# 如果wine是一张表，应该长这样：
import pandas as pd

train = pd.read_csv('dt.csv',encoding='gbk')

train['职业分类'] = train['职业分类'].map(
    {'金融':5,'行政':4,'司法':3,'IT':2,'教育':1}
)
train['职位评级'] = train['职位评级'].map(
	{'A类':3, 'B类':2, 'C类':1}
)
train['债务情况'] = train['债务情况'].map(
	{'低':3, '中':2, '高':1}
)

train_Label = pd.DataFrame(train['类别'])
train.drop('类别',axis=1,inplace=True)
print(train)
# train.to_csv("tzzs_data2.csv",encoding='gbk')
# 切分训练集和测试集
# 训练集是随机划分的，所以每次运行结果可能不一样
Xtrain, Xtest, Ytrain, Ytest = train_test_split(train,train_Label,test_size=0.2)

# 建立模型
clf = tree.DecisionTreeClassifier(criterion="entropy",min_samples_leaf=3)
#clf = tree.DecisionTreeClassifier(criterion="gini")
clf = clf.fit(Xtrain, Ytrain)
#clf = clf.fit(Xtrain, Ytrain)
score = clf.score(Xtest, Ytest) #返回预测的准确度
print("score",score)

# 
# 绘制树
import graphviz
feature_name = ['职业分类','职位评级','收入','有房有车','债务情况']

dot_data = tree.export_graphviz(clf
	,out_file=None
	,feature_names= feature_name
	,class_names=["钻石男","经适男","牛奋男"]
	,filled=True
	,rounded=True
	)
graph = graphviz.Source(dot_data.replace("helvetica","FangSong"))
graph.view()

