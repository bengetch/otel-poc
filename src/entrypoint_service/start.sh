#!/bin/bash

exec opentelemetry-instrument \
  --traces_exporter console \
  --metrics_exporter console \
  --logs_exporter console \
  --service_name entrypoint_service \
  flask run