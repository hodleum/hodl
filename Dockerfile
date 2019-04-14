FROM ubuntu
WORKDIR /home
RUN apt update && apt install -y git sqlite python3-dev python3-pip python3
RUN mkdir hodl
RUN pip3 install pycryptodome v8-cffi sqlalchemy
RUN pip3 install json5 twisted
RUN pip3 install mmh3 werkzeug coloredlogs upnpclient toml
WORKDIR /home/hodl
