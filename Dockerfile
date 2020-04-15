FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

MAINTAINER mm6@sanger.ac.uk

RUN apt-get -qq update
RUN apt-get install --no-install-recommends -y
RUN apt-get install --quiet --assume-yes git python python-pip
RUN pip install setuptools mock
RUN mkdir -p /opt
WORKDIR /opt
RUN git clone https://github.com/sanger-pathogens/PathPipeConfTools.git
ENV  BUILD_DIR /opt/PathPipeConfTools
WORKDIR ${BUILD_DIR}
COPY README.md README.rst
RUN python setup.py install
RUN ./run_tests.sh

CMD list-pathogen-pipeline-jobs
