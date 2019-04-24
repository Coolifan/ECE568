FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /amazon_server
WORKDIR /amazon_server
ADD requirements.txt /amazon_server/
RUN pip install -r requirements.txt
ADD . /amazon_server/
