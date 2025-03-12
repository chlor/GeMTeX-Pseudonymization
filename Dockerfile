FROM python:3.11-slim-buster

ARG VERSION=${0.3.0}

WORKDIR /.

RUN pip install -r requirements.txt

RUN python gemtex_surrogator.py --webservice

ENTRYPOINT [ "." ]
