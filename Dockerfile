# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /learning-recommendation

COPY setup.sh setup.sh
COPY requirements.txt requirements.txt

RUN ./setup.sh

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
