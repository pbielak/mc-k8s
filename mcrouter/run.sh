#!/bin/bash

echo "Starting ConfigUpdater..."

# Start Config Updater
python /config_updater/app.py &

while [ ! -f /tmp/mcrouter.conf ]; do
  echo "Waiting for initial config file..."
  sleep 1
done

echo "Got config\n--------"
cat /tmp/mcrouter.conf
echo "--------"

# Start mcrouter
mcrouter --constantly-reload-configs --config-file /tmp/mcrouter.conf --port 5000 &

while /bin/true; do
  ps aux |grep python |grep -q -v grep
  PROCESS_1_STATUS=$?
  ps aux |grep mcrouter |grep -q -v grep
  PROCESS_2_STATUS=$?

  if [ $PROCESS_1_STATUS -ne 0 -o $PROCESS_2_STATUS -ne 0 ]; then
    echo "One of the processes has already exited."
    exit -1
  fi
  sleep 60
done
