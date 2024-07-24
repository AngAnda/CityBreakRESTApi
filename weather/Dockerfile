FROM python

ENV REDIS_HOST=redis
ADD . /opt/weather

WORKDIR /opt/weather

RUN pip install -r requirements

EXPOSE 5000

CMD ["python", "main.py"]
