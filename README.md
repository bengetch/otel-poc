# otel-poc
PoC OTel implementation

# Usage

Inside the `src` directory, create a `.env` file that matches the `.env.example` file. The contents can be 
identical to those in the `.env.example` file. Note also that the `.env` file that you create will be distinct
from the existing `common.env` file, which should not be modified. The `docker-compose.yml` file in this directory 
defines 4 services:

1. An `entrypoint` service that functions as a public API for testing functionalities.
2. Two "microservices", `service_a` and `service_b`, which get called by the `entrypoint` service and can
do arbitrary work.
3. A `collector` service that receives and stores metrics, traces, and logs from the `entrypoint` service.
    * Note that it is possible to have `service_a` and `service_b` send their metrics/traces/logs to the 
    `collector` service by following the same configuration as the `entrypoint` service

To deploy the services defined in `docker-compose.yml`, run `docker compose up --build`. 
