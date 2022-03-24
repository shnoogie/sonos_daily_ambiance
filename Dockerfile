FROM alpine:3.14
RUN apk add --no-cache python3 py3-pip git tzdata
RUN git clone https://github.com/shnoogie/sonos_daily_ambiance.git \
    && cd sonos_daily_ambiance \
    && pip3 install -r requirements.txt
WORKDIR sonos_daily_ambiance
CMD ["python3", "app.py"]