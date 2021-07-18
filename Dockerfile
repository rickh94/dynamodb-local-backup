FROM python:3.9
MAINTAINER Rick Henry<rickhenry@rickhenry.dev>

ADD ./requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir /opt/dynamodb-local-backup
ADD src/. /opt/dynamodb-local-backup

WORKDIR /opt/dynamodb-local-backup
