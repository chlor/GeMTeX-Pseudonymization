FROM python:3.11-slim-buster

ARG WEBSERVICE_WORKDIR=/webservice

WORKDIR $WEBSERVICE_WORKDIR

COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "gemtex_surrogator.py" ]
