FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN pip install -U pip
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD . /code/
RUN pip install -r requirements.txt
