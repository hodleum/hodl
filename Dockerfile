FROM frolvlad/alpine-python3
WORKDIR /home
RUN apk update && apk add git sqlite python3-dev build-base
RUN git clone https://github.com/hodleum/hodl.git
RUN pip install pycrypto docker

