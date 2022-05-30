import json

from flask import Flask, jsonify, request
from flask_cors import CORS
from scipy.stats import ks_2samp

app = Flask(__name__)
CORS(app)


@app.route('/ks_test', methods=['POST'])
def ksTest():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    return jsonify(ks_2samp(data['setA'], data['setB']))


if __name__ == '__main__':
    app.debug = False  # 设置调试模式，生产模式的时候要关掉debug
    app.run()
