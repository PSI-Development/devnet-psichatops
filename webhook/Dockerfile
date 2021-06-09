#FROM ubuntu
#RUN apt-get update && \
#    apt-get -y install gcc mono-mcs && \
#    rm -rf /var/lib/apt/lists/*
FROM python:3.7.9-slim
RUN mkdir /opt/devnet_webhook
WORKDIR /opt/devnet_webhook
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .
#EXPOSE 4999
#ENV FLASK_APP=app_webhook.py
#CMD ["python", "./app_webhook.py"]
CMD ["gunicorn", "-w", "3", "-b", ":3999", "-t", "360", "--reload", "wsgi:flask_app"]
