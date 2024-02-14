FROM python:3.8-slim

# set container dir, copy dependencies from host
WORKDIR /usr/src/app
COPY . .

# install python dependencies
RUN pip install -r requirements.txt --no-cache-dir
RUN opentelemetry-bootstrap -a install
RUN chmod +x start.sh

# run container
CMD ["./start.sh"]