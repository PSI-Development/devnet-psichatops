#FROM ubuntu
#RUN apt-get update && \
#    apt-get -y install gcc mono-mcs && \
#    rm -rf /var/lib/apt/lists/*
FROM python:3.7
RUN apt-get update \
  && apt-get install -y --no-install-recommends graphviz \
  && apt-get install -y --no-install-recommends graphviz-dev \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir pyparsing pydot
RUN mkdir /opt/devnet_chatops
WORKDIR /opt/devnet_chatops
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .
#EXPOSE 5000
#ENV FLASK_APP=app_v1.py
#CMD ["python", "./app.py"]
CMD ["gunicorn", "-w", "3", "-b", ":4000", "-t", "360", "--reload", "wsgi:bot"]