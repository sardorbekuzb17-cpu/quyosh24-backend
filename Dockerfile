ARG PYTHON_VERSION=3.14-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

ENV SECRET_KEY "8JSDEJDhjn7EM2FybnIwU06ZHXauW5N9jStW21vHZGW0L7pegC"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn","--bind",":8000","--workers","2","payme_backend.wsgi"]
