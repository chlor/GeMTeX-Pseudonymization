FROM python:3.11-slim-buster

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

ENTRYPOINT [ "python", "gemtex_surrogator.py", "--webservice" ]
