FROM python:3.11-slim-buster

ARG WEBSERVICE_WORKDIR=/webservice

WORKDIR $WEBSERVICE_WORKDIR

COPY gemtex_surrogator.py pyproject.toml ./
COPY GeMTeXSurrogator ./GeMTeXSurrogator/
COPY resources ./resources
RUN pip install .
RUN download_models

ENTRYPOINT [ "python", "gemtex_surrogator.py" ]
