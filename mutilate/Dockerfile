FROM nqnielsen/mutilate-docker

ADD ./mutilate-stresser-script.sh .
RUN chmod +x mutilate-stresser-script.sh

CMD ["/bin/sh", "-c", "./mutilate-stresser-script.sh $MEMCACHED_HOST $MEMCACHED_PORT"]
