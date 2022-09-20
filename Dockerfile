# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /learning-recommendation

RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install default-libmysqlclient-dev -y


COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
