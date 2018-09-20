FROM python:3.6-alpine3.6

RUN apk add --update --no-cache g++ gcc libxslt-dev

ADD . /

RUN pip install -r requirements.txt

CMD ["python","maths-bot.py"]
