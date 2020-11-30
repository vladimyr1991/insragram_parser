FROM python:3.8-slim
RUN apt-get update && apt-get install -y libffi-dev libc-dev && \
    pip3 install -U pip setuptools
RUN apt-get install -y libxml2-dev libxslt-dev
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y python-dev && \
    apt-get install -y python3-dev && \
    apt-get install -y libevent-dev && \
    apt-get update -y && \
    apt-get install -y --reinstall build-essential
WORKDIR /app
COPY ./app /app
RUN apt-get install -y gcc \
    && pip3 install -r requirements.txt \
    && apt-get remove -y gcc && apt-get autoremove -y
CMD ["uwsgi", "/app/uwsgi.ini"]