from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/api', methods=['GET'])
def home():
    # Simulate some logic
    data = {"message": "Hello from Service A"}
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
