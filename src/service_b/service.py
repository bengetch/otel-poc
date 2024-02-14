from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/api', methods=['GET'])
def home():
    data = {"message": "Hello from Service B"}
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
