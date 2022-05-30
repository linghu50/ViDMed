import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import precision_score, accuracy_score, recall_score, roc_curve
import graphviz
from sklearn.model_selection import GridSearchCV
import DataChange
import multiprocessing

def load_file(filename):
    save_name = filename.split('.')[0]
    file_type = filename.split('.')[1]
    if file_type == 'csv':
        df = pd.read_csv(filename)
    elif file_type == 'xlsx':
        df = pd.read_excel(filename)
    else:
        print("Error type")
        return
    return df, save_name

def get_data(df):
    df = DataChange.split_feature(df)
    df = df[df != "NA"]  # 把NA换为null值
    col = df.shape[1]
    df = df.dropna(axis=0, thresh = int(col * 0.7))
    df = df.fillna(0)
    x = df.iloc[:, 1:-1]        # 除去了第一列的病人ID
    y = df.iloc[:, -1]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size= 0.1)
    return x, y, x_train, y_train, x_test, y_test

#模型的评价
def model_s(y_predict,y_test):
    print("正确率为：", np.sum(y_predict == y_test) / len(y_test))
    print("准确率：", accuracy_score(y_test, y_predict))
    print("精确率：", precision_score(y_test, y_predict, average='macro'))  # 多分类问题需要加average选择
    print("查全率：", recall_score(y_test, y_predict, average='macro'))
    """
    # 只有二分类才适用
    fpr, tpr, thresholds = roc_curve(y_test, y_predict)
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.xlim(0,1)
    plt.ylim(0,1)
    plt.title("ROC曲线")
    plt.xlabel("假正比率fpr")
    plt.ylabel("真正比率tpr")
    plt.plot(fpr,tpr,c='r')
    plt.show()
    """
#模型可视化
def model_plot(clf):
    tree.plot_tree(clf)
    plt.show()



def id3(x_train, y_train, x_test, y_test, save_name):
    #id3_tree = tree.DecisionTreeClassifier(criterion="entropy")
    id3_tree = tree.DecisionTreeClassifier(criterion="entropy", min_impurity_decrease=0.0, max_depth=5, min_samples_split=22)
    id3_tree.fit(x_train, y_train.astype('int'))
    y_predict = id3_tree.predict(x_test)

    print(y_predict)

    # 调用模型评价的函数
    model_s(y_predict.astype('int'), y_test.astype('int'))

    # 结果可视化
    feature_name = x_train.columns
    class_name = ['III', 'I', 'II', 'IV']
    tree.plot_tree(id3_tree)
    plt.show()
    dot_data = tree.export_graphviz(id3_tree
                                    , out_file=None
                                    , feature_names = feature_name
                                    , class_names = class_name
                                    , filled = True
                                    , rounded = True)
    graph = graphviz.Source(dot_data)
    graph.render(filename=save_name + '_entropy', view=True)
    #graph.render("try")

def get_ccf_alpha(clf):
    # 以下代码主要目的是找到较优的ccp_alpha,然后就可以在DecisionTreeClassifier类实例化的时候设置ccp_alpha参数为找到的ccp_alpha值。
    path = clf.cost_complexity_pruning_path(x_train, y_train)
    ccp_alphas, impurities = path.ccp_alphas, path.impurities
    print(ccp_alphas)
    '''
    [0.         0.00232752 0.00375587 0.00375587 0.00391236 0.00438185
     0.00629975 0.00730308 0.00946792 0.01198161 0.01788007 0.04055896
     0.31844825]
    '''
    clfs = []
    for ccp_alpha in ccp_alphas:
        clf = DecisionTreeClassifier(random_state=0, ccp_alpha=ccp_alpha)
        clf.fit(x_train, y_train)
        clfs.append(clf)
    print("Number of nodes in the last tree is: {} with ccp_alpha: {}".format(
        clfs[-1].tree_.node_count, ccp_alphas[-1]))

    # 返回：Number of nodes in the last tree is: 1 with ccp_alpha: 0.3184482456829032

    # 绘制不同ccp_alpha取值下，clf在训练样本和测试样本上的精确度
    train_scores = [clf.score(x_train, y_train) for clf in clfs]
    test_scores = [clf.score(x_test, y_test) for clf in clfs]
    from matplotlib import pyplot
    plt.rcParams['savefig.dpi'] = 80  # 图片像素
    plt.rcParams['figure.dpi'] = 200  # 分辨率
    # 默认的像素：[6.0,4.0]，分辨率为100，图片尺寸为 600*400
    fig, ax = pyplot.subplots()
    ax.set_xlabel("alpha")
    ax.set_ylabel("accuracy")
    ax.set_title("Accuracy vs alpha for training and testing sets")
    ax.plot(ccp_alphas, train_scores, marker='o', label="train",
            drawstyle="steps-post")
    ax.plot(ccp_alphas, test_scores, marker='o', label="test",
            drawstyle="steps-post")
    ax.legend()
    pyplot.show()


def get_best(x, y):
    entropy_thresholds = np.linspace(0, 0.1, 10)
    gini_thresholds = np.linspace(0, 0.2, 100)
    ccp_alpha = np.linspace(0, 0.5, 20)
    '''
    {'criterion': ['entropy'], 'min_impurity_decrease': entropy_thresholds},
                  {'criterion': ['gini'], 'min_impurity_decrease': gini_thresholds},
    '''
    # 设置参数矩阵：
    param_grid = {'criterion': ['entropy'], 'max_depth': np.arange(2, 10), 'min_samples_split': np.arange(2, 30, 2), 'ccp_alpha': ccp_alpha, 'min_impurity_decrease': entropy_thresholds}
    clf = GridSearchCV(DecisionTreeClassifier(), param_grid, cv=5)
    clf.fit(x, y)
    print("best param:{0}\nbest score:{1}".format(clf.best_params_, clf.best_score_))

def GetResult(headers, datas, filename, choose, Downfile, target, class_name):
    df = pd.DataFrame(datas, columns=headers)
    #print(df.columns)
    print(choose)
    if (len(choose)):
        use = []
        use.extend(choose)
        if not headers[0] in use:
            use.append(headers[0])
        if not target in use:
            use.append(target)
        print(use)
        df = df[use]
    # num = 5
    # df_pool = []
    # columns = df.columns
    # interval = df.shape[1] // num
    # for i in range(num - 1):
    #     column = columns[i*interval, (i+1)*interval]
    #     df_pool.append(df[column])
    # df_pool.append(df[columns[(num - 1)*interval, df.shape[1]]])
    # jobs = []
    # for i in range(num):
    #     p = multiprocessing.Process(target=DataChange.split_feature, args=(df_pool[i],))
    #     jobs.append(p)
    #     p.start()
    # for p in jobs:
    #     p.join()
    # df_response = [p.get() for p in jobs]
    # df_result = pd.DataFrame()
    # for df_res in df_response:
    #     df_result.join()
    df = DataChange.split_feature(df)
    # df = df[df != "NA"]  # 把NA换为null值
    # col = df.shape[1]
    # df = df.dropna(axis=0, thresh=int(col * 0.7))
    # df = df.fillna(0)
    #print(df)
    x = df.iloc[:, 1:]  # 除去了第一列的病人ID
    y = df[target]
    x = x.drop(columns=target)
    accuracies = []
    precisions = []
    for i in range(5):
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)
        #id3_tree = tree.DecisionTreeClassifier(criterion="entropy")
        id3_tree = tree.DecisionTreeClassifier(criterion="entropy", min_impurity_decrease=0.0, max_depth=5,min_samples_split=22)
        id3_tree.fit(x_train, y_train.astype('int'))
        y_predict = id3_tree.predict(x_test)
        accuracies.append(accuracy_score(y_test, y_predict))
        precisions.append(precision_score(y_test, y_predict, average='macro'))
    print(accuracies, precisions)
    accuracy = "%0.3f" % (np.mean(accuracies))
    #print(accuracy)
    precision = "%0.3f" % (np.mean(precisions))  # 多分类问题需要加average选择
    #print(precision)
    if Downfile:
        feature_name = x_train.columns
        tree.plot_tree(id3_tree)
        dot_data = tree.export_graphviz(id3_tree
                                        , out_file=None
                                        , feature_names=feature_name
                                        , class_names=class_name
                                        , filled=True
                                        , rounded=True)
        graph = graphviz.Source(dot_data)
        graph.render(filename='result/' + filename+ '_' + target, view=False)
    return accuracy, precision


if __name__=='__main__':
    filename = 'oral_num.csv'
    df, save_name = load_file(filename)
    x, y, x_train, y_train, x_test, y_test = get_data(df)
    id3(x_train, y_train, x_test, y_test, save_name)
    # get_best(x, y)