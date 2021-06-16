FROM python:3.9-alpine
MAINTAINER Rick Henry<rickhenry@rickhenry.dev>

ADD ./requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir /opt/dynamodb-local-backup
ADD ./backup.py /opt/dynamodb-local-backup
ADD ./restore.py /opt/dynamodb-local-backup

WORKDIR /opt/dynamodb-local-backup
