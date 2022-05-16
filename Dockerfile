FROM python:3.8-slim
MAINTAINER "michael_semionoff"

RUN apt-get update -y
RUN apt-get install -y --no-install-recommends python3-pip 
RUN pip3 install --upgrade setuptools
RUN pip3 install mongoengine protobuf betterproto grpclib grpcio grpcio-tools
RUN mkdir -p /home/boxes
WORKDIR /home/boxes
COPY . .

EXPOSE 50051
ENTRYPOINT ["python3", "server.py"]