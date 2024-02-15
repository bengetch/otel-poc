#!/bin/bash

exec opentelemetry-instrument \
  --traces_exporter otlp \
  --metrics_exporter otlp \
  --logs_exporter otlp \
  --service_name entrypoint_service \
  flask run