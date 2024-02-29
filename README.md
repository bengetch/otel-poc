# otel-poc
PoC OTel implementation

# Usage

Inside the `src` directory, create a `.env` file that matches the `.env.example` file. The contents should be 
identical to those in the `.env.example` file, except with the `DATADOG_API_KEY` value populated. Note also that 
the `.env` file that you create will be distinct from the existing `common.env` file, which can be modified as 
needed. The `docker-compose.yml` file in this directory defines 4 services:

1. An `entrypoint` service that functions as a public API for testing functionalities.
2. Two "microservices", `service_a` and `service_b`, which get called by the `entrypoint` service and can
   do arbitrary workflows.
3. A `collector` service that receives and stores metrics, traces, and logs from the `entrypoint` service. The
   configuration for this service is defined in `src/otel_collector/collector-config.yml`. By default, all 
   telemetry received by the collector is sent to both stdout and datadog. 

To deploy the services defined in `docker-compose.yml`, run `docker compose up --build`. 

# Modifying telemetry data

By default, all 3 services (`entrypoint`, `service_a`, and `service_b`) send all of their telemetry data to the
`collector`, which then organizes and exports it both to stdout and datadog. This can be modified for situations
where one doesn't want to depend on the `collector` service at all (in which case it can be commented out entirely
in the `docker-compose.yml` file), or where the user wants to mute stdout reporting for any of the three telemetry
types (logs, metrics, traces). The control point for this behavior is via the environment variables `SPAN_EXPORTER`,
`METRICS_EXPORTER`, and `LOGS_EXPORTER` on each service. Each of these variables can be one of the following values:

1. `OTLP`: Send telemetry for this type to the `collector`. The `collector` will still send incoming telemetry for
   this type to stdout.
2. `CONSOLE`: Send telemetry for this type only to the service's stdout, and ignore the `collector`. 
3. `NOOP`: Don't send telemetry for this type anywhere, effectively muting it. 

These environment variables can be set globally (i.e. for all services) in `common.env`. By default, they are all set
to `OTLP`. If you'd like to modify configuration for a single service, you can add an entry in it's `environment`
dictionary in `docker-compose.yml`, which will override any value found in `common.env`.


# Interacting with running services

There are four endpoints on the `entrypoint` service:

1. `hello_service_a`: Calls `service_a`, which returns a simple message.
2. `hello_service_b`: Calls `service_b`, which returns a simple message.
3. `multistep_pattern_one`: Calls `service_a`, which calls `service_b`, then `service_a` returns output from 
   `service_b` to the `entrypoint` service. This workflow is useful for demonstrating trace propagation across
   API endpoints.
4. `multistep_pattern_two`: Calls `service_a`, which calls `service_b`, but immediately returns a status code to
   the `entrypoint` service without waiting for the response from `service_b`. 

All of these endpoints can be called via the following:
```python
import requests
resp = requests.get("http://127.0.0.1:5000/<ENDPOINT-NAME>")
```