FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update && \
	apt-get install --no-install-recommends -y && \
	apt-get install --quiet --assume-yes python python-pip && \
	pip install setuptools mock

ENV  BUILD_DIR /opt/PathPipeConfTools
RUN mkdir -p ${BUILD_DIR}
COPY . ${BUILD_DIR}
WORKDIR ${BUILD_DIR}

RUN python setup.py install && \
	apt-get clean all

CMD list-pathogen-pipeline-jobs
