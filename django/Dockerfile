FROM python:3.8
ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

CMD uwsgi --socket /shared/django.sock --module myrecipe.wsgi
