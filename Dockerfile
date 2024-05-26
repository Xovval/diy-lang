FROM python:3.8

RUN apt update \
    && apt install -y inotify-tools \
    && pip3 install nose \
    && rm -rf /var/lib/apt/lists /var/cache/apt/archives

RUN mkdir /app
WORKDIR /app

CMD [ "./run-tests.sh" ]
