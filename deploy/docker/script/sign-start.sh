#!/usr/bin/env bash

# sql start with
# mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e 'use ${WEBASE_DB_NAME}'
# init db if not exist
echo "check database of ${WEBASE_DB_NAME}"
echo "using u ${WEBASE_DB_UNAME} p ${WEBASE_DB_PWD} -h ${WEBASE_DB_IP} -P ${WEBASE_DB_PORT}"
useCommand="use ${WEBASE_DB_NAME}"
createCommand="create database ${WEBASE_DB_NAME}"
echo "run command: [mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e ${useCommand}]"
echo "run command: [mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e ${createCommand}]"
if ! mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e ${useCommand}; then
    # if return 1(db not exist), create db
    echo "now create database [${WEBASE_DB_NAME}]"
    if mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e ${createCommand}; then
        echo "create database success!"
    fi
fi

# this script used in docker-compose
echo "start webase-sign now..."
java ${JAVA_OPTS} -Djdk.tls.namedGroups="secp256k1", -Duser.timezone="Asia/Shanghai" -Djava.security.egd=file:/dev/./urandom, -Djava.library.path=/dist/conf -cp ${CLASSPATH}  ${APP_MAIN}