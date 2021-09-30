#!/usr/bin/env bash

# sql start with
# mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e 'use ${WEBASE_DB_NAME}'
# init db if not exist
echo "check database of ${WEBASE_DB_NAME}"
echo "using u ${WEBASE_DB_UNAME} p ${WEBASE_DB_PWD} -h ${WEBASE_DB_IP} -P ${WEBASE_DB_PORT}"
useCommand="use ${WEBASE_DB_NAME}"
createCommand="create database ${WEBASE_DB_NAME} default character set utf8;"
# echo "run command: [mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e ${useCommand}]"
# echo "run command: [mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} -e ${createCommand}]"


while true ; do
    #command
    sleep 1
    echo "check mysql status..."
    echo "select version();" | mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} 
    if [ $? == 0 ] ; then
        echo "======== mysql is on"
        break;
    else
        (( ex_count = ${ex_count} + 1 ))
        echo "Waiting mysql to start! ex_count = ${ex_count}."
        if [ ${ex_count} -ge 10 ]; then
            echo "======== Connect to mysql timeout failed!"
            break;
        fi
    fi
done

echo "${useCommand}" | mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} 
if [ $? == 0 ]; then
    echo "database of [${WEBASE_DB_UNAME}] already exist, skip init"
else
    # if return 1(db not exist), create db
    echo "now create database [${WEBASE_DB_NAME}]"
    echo "${createCommand}" | mysql -u${WEBASE_DB_UNAME} -p${WEBASE_DB_PWD} -h${WEBASE_DB_IP} -P${WEBASE_DB_PORT} --default-character-set=utf8
    if [ $? == 0 ]; then
        echo "========create database success!"
    else
        echo "======== create database of [${WEBASE_DB_NAME}] failed!"
    fi
fi

# this script used in docker-compose
echo "start webase-sign now..."
java ${JAVA_OPTS} -Djdk.tls.namedGroups="secp256k1", -Duser.timezone="Asia/Shanghai" -Djava.security.egd=file:/dev/./urandom, -Djava.library.path=/dist/conf -cp ${CLASSPATH}  ${APP_MAIN}