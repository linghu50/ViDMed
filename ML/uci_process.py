# 导入数据分析常用库
import graphviz
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import precision_score, accuracy_score, confusion_matrix, roc_curve, roc_auc_score

heart = pd.read_csv('T2DM.csv')
# plt.figure(figsize=(12,10))
# corr = heart.corr()
# sns.heatmap(data=corr, annot=True, square=True, fmt='.2f')
# plt.show()

# # 采用get_dummies()编码方式处理非连续性分类数据
#
# cp_dummies= pd.get_dummies(heart['cp'],prefix = 'cp')
# restecg_dummies =  pd.get_dummies(heart['restecg'],prefix='restecg')
# slope_dummies =  pd.get_dummies(heart['slope'],prefix='slope')
# thal_dummies = pd.get_dummies(heart['thal'],prefix='thal')
#
# # 将原数据中经过独热编码的列删除
# heart_new =  heart.drop(['cp','restecg','slope','thal'],axis=1)
# heart_new = pd.concat([heart_new,cp_dummies,restecg_dummies,slope_dummies,thal_dummies],axis=1)
# heart_new.head()
# 分离出数据和标签
# label =  heart_new['target']
# data =  heart_new.drop('target',axis=1)


label = heart['t2d_inc']
data =  heart.drop('t2d_inc',axis=1)
data =  data.drop(heart.columns[0],axis=1)
feather_name = data.columns
print(data.columns)

# 数据集合的不同特征之间数据相差有点大，对于SVM、KNN等算法，会产生权重影响，因此需要归一化处理数据
from sklearn.preprocessing import StandardScaler
standardScaler = StandardScaler()
standardScaler.fit(data)
data = standardScaler.transform(data)

# 拆分训练集，测试集
from sklearn.model_selection import train_test_split
train_X,test_X,train_y,test_y = train_test_split(data,label,test_size=0.3)#)

from sklearn.neighbors import KNeighborsClassifier
knn =  KNeighborsClassifier()

#训练数据
knn.fit(train_X,train_y)

# 预测数据
knn_pred_y = knn.predict(test_X)

# 评估模型
print(knn.score(train_X,train_y))

print(knn.score(test_X,test_y))

from sklearn.tree import DecisionTreeClassifier, export_graphviz

tree = DecisionTreeClassifier(criterion="entropy", min_impurity_decrease=0.0, max_depth=5,min_samples_split=22)

# 训练数据
tree.fit(train_X,train_y)

# 预测数据
pred_y = tree.predict(test_X)
print(pred_y)
dot_data = export_graphviz(tree,out_file=None,feature_names=feather_name,class_names=['0','1'],filled=True,rounded=True,special_characters=True)
graph = graphviz.Source(dot_data)
graph.render(filename='try', view=True)

# 评估模型
print(accuracy_score(test_y,pred_y))

print(tree.score(train_X,train_y))

from sklearn.linear_model import LogisticRegression
log_reg= LogisticRegression()

# 训练模型
log_reg .fit(train_X,train_y)

# 预测数据
log_pred_y = log_reg.predict(test_X)

# 评估模型
print(log_reg.score(train_X,train_y))

print(log_reg.score(test_X,test_y))


# 绘制逻辑回归，KNN和决策树的混淆矩阵
i=1
fig1= plt.figure(figsize=(3*5,1*4))

estimator_dict={'Logistic Regression':log_reg,'KNN':knn,'Decision Tree':tree}
for key,estimator in estimator_dict.items():
    # 绘制混淆矩阵
    pred_y =  estimator.predict(test_X)
    matrix = pd.DataFrame(confusion_matrix(test_y,pred_y))
    ax1 = fig1.add_subplot(1,3,i)
    sns.heatmap(matrix,annot=True,cmap='OrRd')
    plt.title('Confusion Matrix -- %s ' % key)
    i+=1
plt.show()


#绘制逻辑回归，KNN和决策树的ROC 曲线并计算AUC 面积
log_score =  log_reg.decision_function(test_X)
knn_score =  knn.predict_proba(test_X)[:,1]
tree_score =  tree.predict_proba(test_X)[:,1]
score = [log_score,knn_score,tree_score]
i=0
j=1
fig2 = plt.figure(figsize=(4*5,1*4))
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
for key,estimator in estimator_dict.items():
    pred_y =  estimator.predict(test_X)
    ax2 = fig2.add_subplot(1,4,j)
    fprs,tprs,thresholds = roc_curve(test_y,score[i])
    plt.plot(fprs,tprs)
    plt.plot([0,1],linestyle='--')
    area = roc_auc_score(test_y,pred_y)
    plt.xlabel('FP rate\n %s_AUC:%f' % (key,area),fontsize=12)
    plt.ylabel('TP rate',fontsize=12)
    plt.title('ROC of %s 曲线 ' % key,fontsize=14)
    plt.grid()
    i +=1
    j +=1

    #将多个曲线汇总在一张图上
    ax3 =  fig2.add_subplot(1,4,4)
    plt.plot(fprs,tprs,label=key)

    plt.xlabel('FP rate' ,fontsize=12)
    plt.ylabel('TP rate',fontsize=12)
    plt.title('ROC of 曲线 ' ,fontsize=14)


    # 添加网格线
    plt.grid()
    plt.legend()
plt.show()