FROM ubuntu

RUN apt-get update && apt-get install wine-stable wget
RUN wget https://www.python.org/ftp/python/3.7.3/python-3.7.3.exe
RUN wine python-3.7.3.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
