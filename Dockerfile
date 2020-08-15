FROM python:3.7-alpine

COPY bots/config.py /bots/
COPY bots/BBTwitterBot.py /bots/
COPY requirements.txt /tmp
RUN apk add --update --no-cache g++ gcc libxslt-dev libxml2-dev
RUN pip3 install -r /tmp/requirements.txt

WORKDIR /bots
CMD ["python3", "BBTwitterBot.py"]