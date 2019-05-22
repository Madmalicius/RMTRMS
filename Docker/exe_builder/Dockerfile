FROM ubuntu

RUN apt-get update && apt-get install wine-stable python3 python3-pip -y
RUN pip3 install pipenv

#required for pipenv
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8