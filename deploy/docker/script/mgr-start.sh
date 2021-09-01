#!/usr/bin/env bash

# sql start with
# mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e 'use ${WEBASE_DB_NAME}'
# init db if not exist
echo "check database of ${WEBASE_DB_NAME}"
echo "using u ${WEBASE_DB_UNAME} p ${WEBASE_DB_PWD} -h ${WEBASE_DB_IP} -P ${WEBASE_DB_PORT}"

useCommand="'use ${WEBASE_DB_NAME}'"
createCommand="create database ${WEBASE_DB_NAME}"
# echo "run command: [mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e ${useCommand}]"
# echo "run command: [mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e ${createCommand}]"

if mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e ${useCommand}; then
    # if return 1(db not exist), create db
    echo "now create database [${WEBASE_DB_NAME}]"
    if echo "${createCommand}" | mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT}; then
        echo "create database success!"
        echo "now create tables"
        # sed /dist/script/webase.sh
        # sed -i "s:defaultAccount:${WEBASE_DB_UNAME}:g" /dist/script/webase.sh
        # sed -i "s:defaultPassword:${WEBASE_DB_PWD}:g" /dist/script/webase.sh
        # create table
        if mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -D ${WEBASE_DB_NAME} -e "source /dist/script/webase-ddl.sql"; then
            echo "now init table data"
            mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -D ${WEBASE_DB_NAME} -e "source /dist/script/webase-dml.sql"
        fi        
    fi
fi


# this script used in docker-compose
echo "start webase-node-mgr now..."
java ${JAVA_OPTS} -Djdk.tls.namedGroups="secp256k1", -Duser.timezone="Asia/Shanghai" -Djava.security.egd=file:/dev/./urandom, -Djava.library.path=/dist/conf -cp ${CLASSPATH}  ${APP_MAIN}