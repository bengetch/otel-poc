import logging
import random
import time
from flask import Flask, jsonify
from exporters import resolve_span_exporter, resolve_metrics_exporter, resolve_logs_exporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

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
    data = {"message": "Hello from Service B"}
    logger.info("Inside /hello of service B")
    return jsonify(data)


@app.route('/b_multistep_one', methods=['GET'])
def multistep_pattern_one():
    with tracer.start_as_current_span("service_b_multistep_one") as request_span:
        rand_int = random.randint(0, 10)
        request_span.set_attribute("service_b.multistep_pattern_one.random_int", rand_int)
        data = {"message": rand_int}
        return jsonify(data)


@app.route('/b_multistep_two', methods=['GET'])
def multistep_pattern_two():
    with tracer.start_as_current_span("service_b_waiting") as request_span:
        time.sleep(30)
        request_span.set_attribute("service_b.task.waited", True)
        return "", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
