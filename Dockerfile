FROM python:3.9-alpine

RUN apk update
RUN apk --no-cache add openssl-dev gcc libffi-dev linux-headers musl-dev
RUN pip install setuptools prometheus_client google-api-python-client cryptography cffi pyOpenSSL bios
RUN pip install --upgrade oauth2client

ENV BIND_PORT 9173

ADD . /usr/src/app
WORKDIR /usr/src/app

CMD ["python", "gar_exporter.py"]
