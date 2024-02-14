FROM python:3.8-slim

# set container dir, copy dependencies from host
WORKDIR /usr/src/app
COPY . .

# install python dependencies
RUN pip install -r requirements.txt --no-cache-dir

# run container
CMD ["flask", "run"]
