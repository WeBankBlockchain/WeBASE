#!/usr/bin/env bash

# this script used in docker-compose
echo "start webase-front now..."
cp -r /dist/sdk/* /dist/conf/
echo "finish copy sdk files to front's conf dir"
java ${JAVA_OPTS} -Djdk.tls.namedGroups="secp256k1", -Duser.timezone="Asia/Shanghai" -Djava.security.egd=file:/dev/./urandom, -Djava.library.path=/dist/conf -cp ${CLASSPATH}  ${APP_MAIN}