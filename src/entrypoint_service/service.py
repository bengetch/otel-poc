from flask import Flask, jsonify
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/call_service_a', methods=['GET'])
def call_service_a():
    response = requests.get('http://service_a:5001/api')
    logger.info(f"Response from service a: {response}")
    return jsonify(response.json())


@app.route('/call_service_b', methods=['GET'])
def call_service_b():
    response = requests.get('http://service_b:5002/api')
    logger.info(f"Response from service b: {response}")
    return jsonify(response.json())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
