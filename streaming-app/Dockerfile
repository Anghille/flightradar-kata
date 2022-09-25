# get the base docker image. Using alpine for smallest image footprint
FROM alpine:3.16.2

# Set environment variable below in order to force the stdout and stderr streams to be unbuffered
ENV PYTHONUNBUFFERED=1

# Install python
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip

RUN mkdir /run
WORKDIR /run

COPY ./app/kafka-flight-
