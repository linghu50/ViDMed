import sys
import csv
import json
from scipy.io import loadmat


def dataParse2Json(data='matlab.mat', save_path='feature.json'):
    '''
    将.mat文件转化为json文件
    '''
    mat = loadmat(data)
    print()

dataParse2Json()
