FROM ubuntu

RUN apt-get update && apt-get -y install curl
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g limedocs-wiki-converter