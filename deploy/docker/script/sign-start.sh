#!/usr/bin/env bash

# sql start with
# mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e 'use ${WEBASE_DB_NAME}'
# init db if not exist
echo "check database of ${WEBASE_DB_NAME}"
if ! mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e 'use ${WEBASE_DB_NAME}'; then
    # if return 1(db not exist), create db
    echo "now create database [${WEBASE_DB_NAME}]"
    if mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e 'create database ${WEBASE_DB_NAME}'; then
        echo "create database success!"
    fi
fi

# this script used in docker-compose
echo "start webase-sign now..."
java ${JAVA_OPTS} -Djdk.tls.namedGroups="secp256k1", -Duser.timezone="Asia/Shanghai" -Djava.security.egd=file:/dev/./urandom, -Djava.library.path=/dist/conf -cp ${CLASSPATH}  ${APP_MAIN}