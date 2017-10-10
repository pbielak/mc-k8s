MEMCACHED_SERVER=${1}:${2}
echo "Got memcached server = ${MEMCACHED_SERVER}"

./mutilate -s ${MEMCACHED_SERVER} --loadonly

while true;
do ./mutilate -s ${MEMCACHED_SERVER} --noload \
	-B -T 16 -Q 1000 -D 4 -C 4 \
	-c 4 -q 50000 --scan=1000:50000:1000;
sleep 1; done
