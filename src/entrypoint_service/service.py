import logging
import time
import requests
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


service_a_request_counter = meter.create_counter(
    "entrypoint_service.service_a_requests",
    description="The number of requests to service A",
)

service_b_request_counter = meter.create_counter(
    "entrypoint_service.service_b_requests",
    description="The number of requests to service B",
)


@app.route('/hello_service_a', methods=['GET'])
def hello_service_a():

    # create a new span that is the child of whichever the current one is
    with tracer.start_as_current_span("response_hello_a") as request_span:
        response = requests.get("http://service_a:5001/hello")

        # record some state in this span
        request_span.set_attribute("entrypoint_service.hello_service_a.time", str(time.time()))
        # add to the counter we created above
        service_a_request_counter.add(1, {"response.status": response.status_code})

        logger.info(f"Response from service a: {response}")

    return jsonify(response.json())


@app.route('/hello_service_b', methods=['GET'])
def hello_service_b():

    # create a new span that is the child of whichever the current one is
    with tracer.start_as_current_span("response_hello_b") as request_span:
        response = requests.get("http://service_b:5002/hello")

        # record some state in this span
        request_span.set_attribute("entrypoint_service.hello_service_b.time", str(time.time()))

        # add to the counter we created above
        service_b_request_counter.add(1, {"response.status": response.status_code})

        logger.info(f"Response from service b: {response}")

    return jsonify(response.json())


@app.route('/multistep_pattern_one', methods=['GET'])
def multistep_pattern_one():

    with tracer.start_as_current_span("multistep_pattern_one_response") as request_span:
        response = requests.get("http://service_a:5001/a_multistep_one")
        request_span.set_attribute("entrypoint_service.multistep_pattern_one.response", response.json().get("message"))
        return jsonify(response.json())


@app.route('/multistep_pattern_two', methods=['GET'])
def multistep_pattern_two():
    with tracer.start_as_current_span("multistep_pattern_two_response") as request_span:
        response = requests.get("http://service_a:5001/a_multistep_two")
        request_span.set_attribute("entrypoint_service.multistep_pattern_two.response", response.status_code)
        return jsonify({"response": response.status_code})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
