# get the base docker image. Using alpine for smallest image footprint
FROM alpine:3.16.2

# Set environment variable below in order to force the stdout and stderr streams to be unbuffered
ENV PYTHONUNBUFFERED=1

# Install python
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip

# Create file where data is set
RUN mkdir /input
RUN mkdir /collector
WORKDIR /collector

# Install python dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir -r ./requirements.txt
RUN rm ./requirements.txt

# get python collector script
COPY collector.py ./

# Execute python collector
ENTRYPOINT ["python3", "./collector.py"]

