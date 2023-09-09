FROM ubuntu:22.04

COPY . PID_Regulators

RUN apt-get update \
    && apt-get -y install --no-install-recommends python3 \
    && apt-get -y install --no-install-recommends python3-pip \
    && cd PID_Regulators && pip3 install -r requirements.txt
