FROM python


ENV EVENTS_SERVICE_URL=localhost
ENV WEATHER_SERVICE_URL=localhost

ENV DB_HOST=localhost
ENV DB_USER=auth
ENV DB_PASSWORD=abc123

ADD . /opt/auth

WORKDIR /opt/auth

RUN pip install -r requirements

EXPOSE 5000

CMD ["python", "main.py"]
