FROM python:3.6-alpine
RUN apk add --no-cache curl-dev python3-dev libressl-dev gcc g++ \
    && pip install --upgrade pip \
    && pip install prometheus_client pycurl flask pyyaml
