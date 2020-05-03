FROM python:3.7.7-alpine3.11

RUN apk update \
    && apk add \
    build-base \
    postgresql \
    postgresql-dev \
    libpq 

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED 1
ENV FLASK_APP casting.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_ENV development

EXPOSE 5000

ENTRYPOINT ["flask", "run"]