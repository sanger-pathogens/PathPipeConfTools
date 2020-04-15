FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

MAINTAINER mm6@sanger.ac.uk

RUN apt-get -qq update
RUN apt-get install --no-install-recommends -y
RUN apt-get install --quiet --assume-yes git python python-pip
RUN pip install setuptools mock

ENV  BUILD_DIR /opt/PathPipeConfTools
RUN mkdir -p ${BUILD_DIR}
COPY . ${BUILD_DIR}
WORKDIR ${BUILD_DIR}
COPY README.md README.rst

RUN python setup.py install
RUN ./run_tests.sh

CMD list-pathogen-pipeline-jobs
