#!/usr/bin/env bash

# this script used in docker-compose
echo "start webase-web now..."
nginx -c /data/webase-web/nginx/nginx.conf -g 'daemon off;'