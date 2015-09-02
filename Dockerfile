FROM python:2.7
WORKDIR /src
COPY req.pip /src/
COPY src/database /src/database
RUN apt-get install -y libmysqlclient-dev
RUN pip install -r req.pip