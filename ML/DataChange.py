import pandas as pd
import numpy as np
import random

def split_feature(df):
    columns = df.columns
    for column in columns:
        if df[column].astype(str).str.contains(',').any():
            df_one = df[df[column].astype(str).str.contains(',')]
            for i in df_one.index:
                for value in df_one.loc[[i]][column].values[0]:
                    one = df_one.loc[[i]]
                    one[column] = value
                    df = df.append(one, ignore_index=True)  # 一定要加一个ignore_index=True，不然序号会重复，下一步会被一起删除
            df = df.drop(np.array(df[df[column].astype(str).str.contains(',')].index))
        #print(column)
    df = df.reset_index(drop=True)
    return df

def data_map(filename):
    df = pd.read_csv(filename)
    df['occupation'] = df['occupation'].map(
        {'farmer': 1, 'UrbanResident': 2, 'Officer': 3, 'worker': 4, 'others': 5, 'NA': 5})
    df['gender'] = df['gender'].map({'Male': 1, 'Female': 2, 'NA': random.randint(1, 2)})
    df['type.II.respiratory.failure'] = df['type.II.respiratory.failure'].map({'NonTypeII': 1, 'TypeII': 2, 'NA': 1})
    df['consciousness'] = df['consciousness'].map(
        {'Clear': 1, 'ResponsiveToSound': 2, 'ResponsiveToPain': 3, 'Nonresponsive': 4})
    df['respiratory.support.'] = df['respiratory.support.'].map({'None': 1, 'IMV': 2, 'NIMV': 3})
    df['oxygen.inhalation'] = df['oxygen.inhalation'].map({'OxygenTherapy': 1, 'AmbientAir': 2})
    df['outcome.during.hospitalization'] = df['outcome.during.hospitalization'].map(
        {'Alive': 1, 'DischargeAgainstOrder': 2})
    df['ageCat'] = df['ageCat'].map(
        {'(21,29]': 1, '(29,39]': 2, '(39,49]': 3, '(49,59]': 4, '(59,69]': 5, '(69,79]': 6, '(79,89]': 7,
         '(89,110]': 8})
    df['acute.renal.failure']=df['acute.renal.failure'].map({'0':1,'1':2})
    df['Killip.grade'] = df['Killip.grade'].map({'I': 1, 'II': 2, 'III': 3, 'IV': 4})
    df = df.drop(np.array(df[df['Killip.grade'].isnull()].index))
    df = df.fillna(0)
    # 这次的处理是是缺失值为0,1是一般的正常值，性别随机
    df.to_csv('数值版.csv',index=False)


if __name__ == '__main__':
    #df = pd.read_csv('debug-pandas.csv')
    #df = split_feature(df)
    #df.to_csv('test-result.csv', index=False)
    data_map('数值版本.csv')