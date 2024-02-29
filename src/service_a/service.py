import logging
import time
from flask import Flask, jsonify
from exporters import resolve_span_exporter, resolve_metrics_exporter, resolve_logs_exporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import requests
import threading

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# instrumentation for flask and requests - both of these are required for trace propagation across APIs
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# get tracer
tracer = resolve_span_exporter()
# get meter
meter = resolve_metrics_exporter()
# configure log exporter
handler = resolve_logs_exporter()
logger.addHandler(handler)


@app.route('/hello', methods=['GET'])
def hello():
    with tracer.start_as_current_span("service_a_hello") as request_span:

        # record some state in this span
        request_span.set_attribute("service_a.hello.time", str(time.time()))

        logger.info("Inside /hello of service A")

        data = {"message": "Hello from Service A"}
        return jsonify(data)


@app.route('/a_multistep_one', methods=['GET'])
def multistep_pattern_one():
    with tracer.start_as_current_span("service_a_multistep_one") as request_span:
        response = requests.get("http://service_b:5002/b_multistep_one")
        request_span.set_attribute("service_a.multistep_pattern_one.response", response.json().get("message"))
        return jsonify(response.json())


def call_b():
    with tracer.start_as_current_span("service_a_waiting") as request_span:
        requests.get("http://service_b:5002/b_multistep_two")
        request_span.set_attribute("service_a.waited", True)


@app.route('/a_multistep_two', methods=['GET'])
def multistep_pattern_two():
    with tracer.start_as_current_span("service_a_multistep_two") as request_span:
        thread = threading.Thread(target=call_b)
        thread.start()
        return "", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
