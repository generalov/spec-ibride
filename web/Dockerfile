FROM python:2.7
RUN echo 'Acquire::HTTP::Proxy "http://172.17.0.1:3142";' >> /etc/apt/apt.conf.d/01proxy \
     && echo 'Acquire::HTTPS::Proxy "false";' >> /etc/apt/apt.conf.d/01proxy
RUN apt-get update && apt-get install -y mysql-client
ENV PYTHONUNBUFFERED 1
ENV PIP_HOST=172.17.0.1
ENV PIP_INDEX_URL=http://${PIP_HOST}:3141/root/pypi/+simple/ PIP_TRUSTED_HOST=${PIP_HOST}
RUN pip install -U pip
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD . /code/
RUN pip install -r requirements.txt
ENV PIP_HOST= PIP_INDEX_URL=
