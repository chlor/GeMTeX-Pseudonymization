FROM python:3.11-slim-buster

ARG WEBSERVICE_WORKDIR=/webservice

WORKDIR $WEBSERVICE_WORKDIR

COPY . .
RUN pip install . \
    && python -m spacy download de_core_news_lg

ENTRYPOINT [ "python", "gemtex_surrogator.py" ]
