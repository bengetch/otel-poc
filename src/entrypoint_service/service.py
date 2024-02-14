import logging
from flask import Flask, jsonify
from opentelemetry import trace
from opentelemetry import metrics
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# get tracer and meter
tracer = trace.get_tracer("entrypoint_service.tracer")
meter = metrics.get_meter("entrypoint_service.meter")

service_a_request_counter = meter.create_counter(
    "service_a.requests",
    description="The number of requests to service A",
)

# TODO: should I be naming the spans in call_service_a() and call_service_b() differently?
#   It doesnt result in errors at runtime but it might be useful to disambiguate them for later


@app.route('/call_service_a', methods=['GET'])
def call_service_a():

    # create a new span that is the child of whichever the current one is
    with tracer.start_as_current_span("response") as request_span:
        response = requests.get('http://service_a:5001/api')

        # record some state in this span
        request_span.set_attribute("response.status", response.status_code)
        # add to the counter we created above
        service_a_request_counter.add(1, {"response.status": response.status_code})

        logger.info(f"Response from service a: {response}")

    return jsonify(response.json())


@app.route('/call_service_b', methods=['GET'])
def call_service_b():

    # create a new span that is the child of whichever the current one is
    with tracer.start_as_current_span("response") as request_span:
        response = requests.get('http://service_b:5002/api')

        # record some state in this span
        request_span.set_attribute("response.status", response.status_code)
        # add to the counter we created above
        service_a_request_counter.add(1, {"response.status": response.status_code})

        logger.info(f"Response from service b: {response}")

    return jsonify(response.json())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
