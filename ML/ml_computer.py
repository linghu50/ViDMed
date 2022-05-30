# 导入数据分析常用库
import matplotlib

import DataChange

matplotlib.use('Agg')
import graphviz
import numpy as np
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

from sklearn import tree
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import precision_score, accuracy_score, confusion_matrix, roc_curve, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


def GetHeatmap(headers, datas, choose, target):
    df = pd.DataFrame(datas, columns=headers)
    if (len(choose)):
        use = []
        use.extend(choose)
        if not target in use:
            use.append(target)
        df = df[use]
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 这两行用来显示汉字
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure()
    sio = BytesIO()
    corr = df.corr()
    # 如果想都是一边vmin=corr.values.min(), vmax=1,
    sns.heatmap(data=corr, square=True, cmap="YlGnBu", linewidths=0.1, annot=True, annot_kws={"fontsize":8}, fmt='.2f')
    plt.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
    data = base64.encodebytes(sio.getvalue()).decode()
    src = 'data:image/png;base64,' + str(data)
    # 记得关闭，不然画出来的图是重复的
    plt.close()
    return src

def GetKNN(headers, datas, choose, target, class_name, language):
    df = pd.DataFrame(datas, columns=headers)
    print(choose)
    if (len(choose)):
        use = []
        use.extend(choose)
        if not target in use:
            use.append(target)
        print(use)
        df = df[use]
    df = DataChange.split_feature(df)
    label = df[target]
    data = df.drop(columns=target)
    train_X,test_X,train_y,test_y = train_test_split(data, label, test_size=0.3)
    knn = KNeighborsClassifier()
    knn.fit(train_X,train_y)
    knn_pred_y = knn.predict(test_X)
    accuracy = "%0.3f" % (accuracy_score(test_y, knn_pred_y))
    precision = "%0.3f" % (precision_score(test_y, knn_pred_y, average='macro'))
    sio = BytesIO()
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 这两行用来显示汉字
    plt.rcParams['axes.unicode_minus'] = False
    fig = plt.figure(figsize=(2*5,1*4))
    matrix = pd.DataFrame(confusion_matrix(test_y, knn_pred_y))
    ax1 = fig.add_subplot(1,2,1)
    sns.heatmap(matrix, annot=True, cmap='OrRd')
    if language == 'zh':
        plt.title('混淆矩阵 -- KNN')
        plt.xlabel('预测值')
        plt.ylabel('真实值')
    else:
        plt.title('Confusion Matrix -- KNN ')
        plt.xlabel('predict')
        plt.ylabel('label')
    if len(class_name) > 2:
        plt.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
        data = base64.encodebytes(sio.getvalue()).decode()
        src = 'data:image/png;base64,' + str(data)
        return accuracy, precision, src
    ax2 = fig.add_subplot(1,2,2)
    fprs, tprs, thresholds = roc_curve(test_y, knn.predict_proba(test_X)[:,1])
    plt.plot(fprs,tprs)
    plt.plot([0, 1], linestyle='--')
    area = roc_auc_score(test_y, knn_pred_y)
    plt.xlabel('FP rate\n KNN_AUC:%f'%area, fontsize=12)
    plt.ylabel('TP rate', fontsize=12)
    plt.title('ROC - KNN', fontsize=14)
    plt.grid()
    plt.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
    data = base64.encodebytes(sio.getvalue()).decode()
    src = 'data:image/png;base64,' + str(data)
    # 记得关闭，不然画出来的图是重复的
    plt.close()
    return accuracy, precision, src

def GetLogistic(headers, datas, choose, target, class_name, language):
    df = pd.DataFrame(datas, columns=headers)
    print(choose)
    if (len(choose)):
        use = []
        use.extend(choose)
        if not target in use:
            use.append(target)
        print(use)
        df = df[use]
    df = DataChange.split_feature(df)
    label = df[target]
    data = df.drop(columns=target)
    train_X,test_X,train_y,test_y = train_test_split(data, label, test_size=0.3)
    logistic = LogisticRegression()
    logistic.fit(train_X,train_y)
    logistic_pred_y = logistic.predict(test_X)
    accuracy = "%0.3f" % (accuracy_score(test_y, logistic_pred_y))
    precision = "%0.3f" % (precision_score(test_y, logistic_pred_y, average='macro'))
    sio = BytesIO()
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 这两行用来显示汉字
    plt.rcParams['axes.unicode_minus'] = False
    fig = plt.figure(figsize=(2*5,1*4))
    matrix = pd.DataFrame(confusion_matrix(test_y, logistic_pred_y))
    ax1 = fig.add_subplot(1,2,1)
    sns.heatmap(matrix, annot=True, cmap='OrRd')
    if language == 'zh':
        plt.title('混淆矩阵 -- 逻辑回归')
        plt.xlabel('预测值')
        plt.ylabel('真实值')
    else:
        plt.title('Confusion Matrix -- logistic ')
        plt.xlabel('predict')
        plt.ylabel('label')
    if len(class_name) > 2:
        plt.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
        data = base64.encodebytes(sio.getvalue()).decode()
        src = 'data:image/png;base64,' + str(data)
        return accuracy, precision, src
    ax2 = fig.add_subplot(1,2,2)
    fprs, tprs, thresholds = roc_curve(test_y, logistic.predict_proba(test_X)[:,1])
    plt.plot(fprs,tprs)
    plt.plot([0, 1], linestyle='--')
    area = roc_auc_score(test_y, logistic_pred_y)
    plt.xlabel('FP rate\n Logistic_AUC:%f'%area, fontsize=12)
    plt.ylabel('TP rate', fontsize=12)
    plt.title('ROC - Logistic', fontsize=14)
    plt.grid()
    plt.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
    data = base64.encodebytes(sio.getvalue()).decode()
    src = 'data:image/png;base64,' + str(data)
    # 记得关闭，不然画出来的图是重复的
    plt.close()
    return accuracy, precision, src

def GetDecision(headers, datas, filename, choose, Downfile, target, class_name, language):
    df = pd.DataFrame(datas, columns=headers)
    print(choose)
    if (len(choose)):
        use = []
        use.extend(choose)
        if not target in use:
            use.append(target)
        print(use)
        df = df[use]
    df = DataChange.split_feature(df)
    label = df[target]
    data = df.drop(columns=target)
    train_X,test_X,train_y,test_y = train_test_split(data, label, test_size=0.3)
    id3_tree = tree.DecisionTreeClassifier(criterion="entropy", min_impurity_decrease=0.0, max_depth=5,min_samples_split=22)
    id3_tree.fit(train_X,train_y.astype('int'))
    tree_pred_y = id3_tree.predict(test_X)
    accuracy = "%0.3f" % (accuracy_score(test_y, tree_pred_y))

    if Downfile:
        feature_name = train_X.columns
        tree.plot_tree(id3_tree)
        dot_data = tree.export_graphviz(id3_tree
                                        , out_file=None
                                        , feature_names=feature_name
                                        , class_names=class_name
                                        , filled=True
                                        , rounded=True)
        graph = graphviz.Source(dot_data)
        graph.render(filename='result/' + filename+ '_' + target, view=False)
        precision = "%0.3f" % (precision_score(test_y, tree_pred_y, average='macro'))
        sio = BytesIO()
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 这两行用来显示汉字
        plt.rcParams['axes.unicode_minus'] = False
        fig = plt.figure(figsize=(2 * 5, 1 * 4))
        matrix = pd.DataFrame(confusion_matrix(test_y, tree_pred_y))
        ax1 = fig.add_subplot(1, 2, 1)
        sns.heatmap(matrix, annot=True, cmap='OrRd')
        if language == 'zh':
            plt.title('混淆矩阵 -- 决策树')
            plt.xlabel('预测值')
            plt.ylabel('真实值')
        else:
            plt.title('Confusion Matrix -- Decision ')
            plt.xlabel('predict')
            plt.ylabel('label')
        if len(class_name) > 2 :
            plt.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
            data = base64.encodebytes(sio.getvalue()).decode()
            src = 'data:image/png;base64,' + str(data)
            return accuracy, precision, src
        ax2 = fig.add_subplot(1, 2, 2)
        fprs, tprs, thresholds = roc_curve(test_y, id3_tree.predict_proba(test_X)[:, 1])
        plt.plot(fprs, tprs)
        plt.plot([0, 1], linestyle='--')
        area = roc_auc_score(test_y, tree_pred_y)
        plt.xlabel('FP rate\n Decision_AUC:%f' % area, fontsize=12)
        plt.ylabel('TP rate', fontsize=12)
        plt.title('ROC - Decision', fontsize=14)
        plt.grid()
        plt.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
        data = base64.encodebytes(sio.getvalue()).decode()
        src = 'data:image/png;base64,' + str(data)
        # 记得关闭，不然画出来的图是重复的
        plt.close()
        return accuracy, precision, src
    else:
        return accuracy, None, None

def ModuleCompare(headers, datas, choose, target, class_name, language):
    df = pd.DataFrame(datas, columns=headers)
    print(choose)
    if (len(choose)):
        use = []
        use.extend(choose)
        if not target in use:
            use.append(target)
        print(use)
        df = df[use]
    df = DataChange.split_feature(df)
    label = df[target]
    data = df.drop(columns=target)
    train_X, test_X, train_y, test_y = train_test_split(data, label, test_size=0.3)
    logistic = LogisticRegression()
    knn = KNeighborsClassifier()
    decision = tree.DecisionTreeClassifier(criterion="entropy", min_impurity_decrease=0.0, max_depth=5,min_samples_split=22)
    i = 1
    sio1 = BytesIO()
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 这两行用来显示汉字
    plt.rcParams['axes.unicode_minus'] = False
    fig1 = plt.figure(figsize=(3 * 5, 1 * 4))
    estimator_dict = {'Logistic Regression': logistic, 'KNN': knn, 'Decision Tree': decision}
    for key, estimator in estimator_dict.items():
        # 绘制混淆矩阵
        estimator.fit(train_X,train_y)
        pred_y = estimator.predict(test_X)
        matrix = pd.DataFrame(confusion_matrix(test_y, pred_y))
        ax1 = fig1.add_subplot(1, 3, i)
        sns.heatmap(matrix, annot=True, cmap='OrRd')
        plt.title('Confusion Matrix -- %s ' % key)
        i += 1
    plt.savefig(sio1, format='png', bbox_inches='tight', pad_inches=0.0)
    plt.close()
    if len(class_name) > 2:
        plt.savefig(sio1, format='png', bbox_inches='tight', pad_inches=0.0)
        data = base64.encodebytes(sio1.getvalue()).decode()
        src = 'data:image/png;base64,' + str(data)
        return src, None
    log_score = logistic.decision_function(test_X)
    knn_score = knn.predict_proba(test_X)[:, 1]
    tree_score = decision.predict_proba(test_X)[:, 1]
    score = [log_score, knn_score, tree_score]
    i = 0
    j = 1
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 这两行用来显示汉字
    plt.rcParams['axes.unicode_minus'] = False
    fig2 = plt.figure(figsize=(4 * 5, 1 * 4))
    sio2 = BytesIO()
    for key, estimator in estimator_dict.items():
        pred_y = estimator.predict(test_X)
        ax2 = fig2.add_subplot(1, 4, j)
        fprs, tprs, thresholds = roc_curve(test_y, score[i])
        plt.plot(fprs, tprs)
        plt.plot([0, 1], linestyle='--')
        area = roc_auc_score(test_y, pred_y)
        plt.xlabel('FP rate\n %s_AUC:%f' % (key, area), fontsize=12)
        plt.ylabel('TP rate', fontsize=12)
        plt.title('ROC of %s ' % key, fontsize=14)
        plt.grid()
        i += 1
        j += 1

        # 将多个曲线汇总在一张图上
        ax3 = fig2.add_subplot(1, 4, 4)
        plt.plot(fprs, tprs, label=key)

        plt.xlabel('FP rate', fontsize=12)
        plt.ylabel('TP rate', fontsize=12)
        plt.title('ROC of ', fontsize=14)

        # 添加网格线
        plt.grid()
        plt.legend()
    plt.savefig(sio2, format='png', bbox_inches='tight', pad_inches=0.0)
    plt.close()
    data1 = base64.encodebytes(sio1.getvalue()).decode()
    src1 = 'data:image/png;base64,' + str(data1)
    data2 = base64.encodebytes(sio2.getvalue()).decode()
    src2 = 'data:image/png;base64,' + str(data2)
    return src1, src2

