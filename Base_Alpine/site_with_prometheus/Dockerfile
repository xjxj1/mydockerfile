FROM dockergoto/flask-prometheus-pycurl:v1

COPY . /app
WORKDIR /app
EXPOSE 5000

RUN chmod +x startup.sh
ENTRYPOINT ["/bin/sh", "startup.sh"]
