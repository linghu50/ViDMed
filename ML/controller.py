from flask import Flask, request, send_file
from flask_cors import CORS
import json
import pandas as pd
import time
import GetFeathers
import ml_computer

app = Flask(__name__)
CORS(app)


@app.route('/test', methods=['post'])
def post_test():
    print(request)
    data = request.get_data()
    data = json.loads(data)
    print(data)
    return 'Hello' + data['name']


@app.route('/getDecision', methods=['POST'])
def GetDecision():
    print("Decision start")
    t1 = time.time()
    data = request.get_data()
    data = json.loads(data)
    tHeader = data['tHeader']
    tData = data['tData']
    Downfile = data['DownFile']
    filename = data['filename']
    choose = data['choose']
    target = data['target']
    print('target', target)
    class_name = data['className']
    language = data['language']
    accuracy, precision,src = ml_computer.GetDecision(tHeader, tData, filename, choose, Downfile, target, class_name, language)
    t2 = time.time()
    print("Time:", t2 - t1)
    print(accuracy, precision)
    response = {"accuracy": accuracy, "precision": precision, "src": src}
    # print(response)
    return response
    # return {"accuracy": accuracy, "precision": precision}

@app.route('/getHeatmap', methods=['POST'])
def GetHeatmap():
    print("heatmap start")
    t1 = time.time()
    data = request.get_data()
    data = json.loads(data)
    # print(data)
    tHeader = data['tHeader']
    tData = data['tData']
    choose = data['choose']
    print(choose)
    target = data['target']
    print('target', target)
    src = ml_computer.GetHeatmap(tHeader, tData, choose, target)
    t2 = time.time()
    print("Time:", t2 - t1)
    response = {"src": src}
    return response

@app.route('/getKNN', methods=['POST'])
def GetKNN():
    print("KNN start")
    t1 = time.time()
    data = request.get_data()
    data = json.loads(data)
    tHeader = data['tHeader']
    tData = data['tData']
    choose = data['choose']
    print(choose)
    target = data['target']
    print('target', target)
    class_name = data['className']
    language = data['language']
    accuracy, precision, src = ml_computer.GetKNN(tHeader, tData, choose, target, class_name, language)
    t2 = time.time()
    print("Time:", t2 - t1)
    response = {"accuracy": accuracy, "precision": precision, "src": src}
    return response

@app.route('/getLogistic', methods=['POST'])
def GetLogistic():
    print("Logistic start")
    t1 = time.time()
    data = request.get_data()
    data = json.loads(data)
    tHeader = data['tHeader']
    tData = data['tData']
    choose = data['choose']
    print(choose)
    target = data['target']
    print('target', target)
    class_name = data['className']
    language = data['language']
    accuracy, precision, src = ml_computer.GetLogistic(tHeader, tData, choose, target, class_name, language)
    t2 = time.time()
    print("Time:", t2 - t1)
    response = {"accuracy": accuracy, "precision": precision, "src": src}
    return response


@app.route('/getCompare', methods=['post'])
def GetCompare():
    print("Compare start")
    t1 = time.time()
    data = request.get_data()
    data = json.loads(data)
    tHeader = data['tHeader']
    tData = data['tData']
    choose = data['choose']
    print(choose)
    target = data['target']
    print('target', target)
    class_name = data['className']
    language = data['language']
    src1, src2 = ml_computer.ModuleCompare(tHeader, tData, choose, target, class_name, language)
    t2 = time.time()
    print("Time:", t2 - t1)
    response = {"src1": src1, "src2": src2}
    return response

@app.route('/DownloadPDF', methods=['post'])
def GetPDF():
    print("Come in")
    t1 = time.time()
    data = request.get_data()
    data = json.loads(data)
    print(data)
    filename = data['filename']
    target = data['target']
    the_file_name = "result/" + filename + '_' + target + '.pdf'
    print(the_file_name)
    t2 = time.time()
    print("Time:", t2 - t1)
    return send_file(the_file_name, as_attachment=True)


@app.route('/PrintCSV', methods=['post'])
def GetCSV():
    t1 = time.time()
    data = request.get_data()
    data = json.loads(data)
    # print(data)
    tHeader = data['tHeader']
    tData = data['tData']
    # print(tData)
    chooseHeader = data['chooseHeader']
    # print(chooseHeader)
    df = pd.DataFrame(tData, columns=tHeader)
    result = df[chooseHeader].to_dict(orient='records')
    t2 = time.time()
    print("Time:", t2 - t1)
    # print(result)
    return {'tData': result}


@app.route('/DownloadCSV', methods=['post'])
def DownloadCSV():
    t1 = time.time()
    data = request.get_data()
    data = json.loads(data)
    # print(data)
    tHeader = data['tHeader']
    tData = data['tData']
    filename = data['filename']
    # print(tData)
    chooseHeader = data['chooseHeader']
    # print(chooseHeader)
    df = pd.DataFrame(tData, columns=tHeader)
    result = df[chooseHeader]
    result.to_csv('/download/' + filename, index=False, header=chooseHeader)
    t2 = time.time()
    print("Time:", t2 - t1)
    return send_file('/download/' + filename, as_attachment=True)


@app.route('/getPrimary', methods=['post'])
def GetPrimary():
    start = time.time()
    data = request.get_data()
    data = json.loads(data)
    # print(data)
    tHeader = data['tHeader']
    tData = data['tData']
    target = data['feather']
    print('目标特征: ', target)
    feat_labels = GetFeathers.getRandomTree(tHeader, tData, target)
    print('筛查结果: ', feat_labels)
    print('Time:', time.time()-start)
    return {'primary': feat_labels}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
