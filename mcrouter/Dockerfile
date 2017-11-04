FROM jamescarr/mcrouter:1.0

MAINTAINER Piotr Bielak <piotrbielak2@gmail.com>

ENV CONFIG_UPDATER_DIR /config_updater

RUN apt-get update && \
    apt-get install -y python-pip && \
    pip install kubernetes

ADD app.py $CONFIG_UPDATER_DIR/
ADD template.conf $CONFIG_UPDATER_DIR/
ADD run.sh .

RUN chmod +x run.sh

CMD ["./run.sh"]
