import pandas as pd
import numpy as np
from sklearn.utils import shuffle
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV
from sklearn.model_selection import train_test_split, cross_val_score,KFold,RepeatedKFold,GridSearchCV
from scipy.stats import pearsonr, ttest_ind, levene
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm

xlsx1_filePath = 'data1.xlsx'
xlsx2_filePath = 'data2.xlsx'
data_1 = pd.read_excel(xlsx1_filePath)
data_2 = pd.read_excel(xlsx2_filePath)
rows_1,__ = data_1.shape
rows_2,__ = data_2.shape
data_1.insert(0,'label',[0]*rows_1)
data_2.insert(0,'label',[1]*rows_2)
data = pd.concat([data_1,data_2])
data = shuffle(data)
data = data.fillna(0)
X = data[data.columns[1:]]
y = data['label']
colNames = X.columns
X = X.astype(np.float64)
X = StandardScaler().fit_transform(X)
X = pd.DataFrame(X)
X.columns = colNames

# t-test for feature selection
index = []
for colName in data.columns[1:]:
    if levene(data_1[colName],data_2[colName])[1] > 0.05:
        if ttest_ind(data_1[colName],data_2[colName])[1] < 0.05:
            index.append(colName)
    else:
        if ttest_ind(data_1[colName],data_2[colName],equal_var = False)[1] < 0.05:
            index.append(colName)
print(len(index))

if 'label' not in index:index = ['label']+index
data_1 = data_1[index]
data_2 = data_2[index]
data = pd.concat([data_1,data_2])
data = shuffle(data)
data.index = range(len(data))
x = data[data.columns[1:]]
y = data['label']
x = x.apply(pd.to_numeric, errors = 'ignore')
colNames = x.columns
x = x.fillna(0)
x = x.astype(np.float64)
x = StandardScaler().fit_transform(x)
x = pd.DataFrame(x)
x.columns = colNames