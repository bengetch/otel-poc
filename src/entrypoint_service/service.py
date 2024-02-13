from flask import Flask, jsonify
import requests

app = Flask(__name__)


# Example endpoint that calls Service A
@app.route('/call_service_a', methods=['GET'])
def call_service_a():
    response = requests.get('http://service_a:5001/api')
    return jsonify(response.json())


# Example endpoint that calls Service B
@app.route('/call_service_b', methods=['GET'])
def call_service_b():
    response = requests.get('http://service_b:5002/api')
    return jsonify(response.json())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
