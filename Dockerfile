FROM frolvlad/alpine-python3
WORKDIR /home
RUN apk update && apk add git sqlite python3-dev build-base
RUN mkdir hodl
RUN pip install pycrypto docker
RUN pip install json5
RUN pip install mmh3
WORKDIR /home/hodl
