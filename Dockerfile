FROM ubuntu:16.04

RUN apt update -y
RUN apt install -y python3
RUN apt install -y python3-pip

RUN pip3 install docopt

