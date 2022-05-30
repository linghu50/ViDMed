import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn import tree
from sklearn.metrics import precision_score, accuracy_score

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def getPearson(headers, datas, target):
    df = pd.DataFrame(datas, columns=headers)
    features = df.corr()[target].abs().sort_values(ascending=False)[:11]
    features.drop(target, axis=0, inplace=True)
    features = features.index
    x = df[features]
    y = df[target]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size= 0.1)
    id3_tree = tree.DecisionTreeClassifier(criterion="entropy", min_impurity_decrease=0.0, max_depth=5,
                                               min_samples_split=22)
    id3_tree.fit(x_train, y_train.astype('int'))
    y_predict = id3_tree.predict(x_test)
    accuracy = "%0.3f" % (accuracy_score(y_test, y_predict))
    #print(accuracy)
    precision = "%0.3f" % (precision_score(y_test, y_predict, average='macro'))  # 多分类问题需要加average选择
    print(accuracy, precision)


def getRandomTree(headers, datas, target):
    df = pd.DataFrame(datas, columns=headers)
    features = df.corr().columns[df.corr()[target].abs() > .05]
    features = features.drop(target)
    if headers[0] in features:
        features = features.drop(headers[0])
    print('第一轮相关度筛查：',features)
    # 使用随机森林模型进行拟合的过程
    X_train = df[features]
    y_train = df[target]
    feat_labels = X_train.columns

    rf = RandomForestRegressor(n_estimators=100, max_depth=None)
    rf_pipe = Pipeline([('imputer', SimpleImputer(strategy='median')), ('standardize', StandardScaler()), ('rf', rf)])
    rf_pipe.fit(X_train, y_train)

    # 根据随机森林模型的拟合结果选择特征
    rf = rf_pipe.__getitem__('rf')
    importance = rf.feature_importances_

    # np.argsort()返回待排序集合从下到大的索引值，[::-1]实现倒序，即最终imp_result内保存的是从大到小的索引值
    imp_result = np.argsort(importance)[::-1][:10]
    # 按重要性从高到低输出属性列名和其重要性
    for i in range(len(imp_result)):
        print("%2d. %-*s %f" % (i + 1, 30, feat_labels[imp_result[i]], importance[imp_result[i]]))

    # 对属性列，按属性重要性从高到低进行排序
    feat_labels = [feat_labels[i] for i in imp_result]
    #print(feat_labels)
    return feat_labels
    '''
    x = df[feat_labels]
    y = df['Killip.grade']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size= 0.1)
    id3_tree = tree.DecisionTreeClassifier(criterion="entropy")
    id3_tree.fit(x_train, y_train.astype('int'))
    y_predict = id3_tree.predict(x_test)
    accuracy = "%0.3f" % (accuracy_score(y_test, y_predict))
    #print(accuracy)
    precision = "%0.3f" % (precision_score(y_test, y_predict, average='macro'))  # 多分类问题需要加average选择
    print(accuracy, precision)
    
    # 绘制特征重要性图像
    plt.title('Feature Importance')
    plt.bar(range(len(imp_result)), importance[imp_result], color='lightblue', align='center')
    plt.xticks(range(len(imp_result)), feat_labels, rotation=90)
    plt.xlim([-1, len(imp_result)])
    plt.tight_layout()
    plt.show()
    '''
