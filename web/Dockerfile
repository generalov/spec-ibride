FROM python:2.7
ENV PYTHONUNBUFFERED 1
WORKDIR /app/web

RUN echo 'Acquire::HTTP::Proxy "http://172.17.0.1:3142";' >> /etc/apt/apt.conf.d/01proxy \
     && echo 'Acquire::HTTPS::Proxy "false";' >> /etc/apt/apt.conf.d/01proxy
RUN apt-get update && apt-get install -y \
        mysql-client \
     && apt-get clean \
     && rm -rf /var/lib/apt/lists/*

ARG PIP_ARGS="-i http://172.17.0.1:3141/root/pypi/+simple/ --trusted-host 172.17.0.1"
COPY requirements.txt /app/web/requirements.txt
RUN pip install $PIP_ARGS -r requirements.txt

COPY . /app/web
RUN pip install $PIP_ARGS -e .
