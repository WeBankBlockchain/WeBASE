#!/bin/bash

# Download webase-micro source code and compile.
build() {
   ZIP_URL="https://github.com/QCTC-chain/WeBASE-Micro/archive/refs/heads/main.zip"
   ZIP_FILE="WeBASE-Micro-main.zip"
   DIR_NAME="WeBASE-Micro-main"

   # Download the zip file
   echo "Downloading the zip file from $ZIP_URL..."
   curl -L -o $ZIP_FILE $ZIP_URL

   # Check if the download was successful
   if [ $? -ne 0 ]; then
       echo "Failed to download the zip file."
       exit 1
   fi

   # Unzip the file
   echo "Unzipping the file..."
   unzip $ZIP_FILE

   # Check if the unzip was successful
   if [ $? -ne 0 ]; then
       echo "Failed to unzip the file."
       exit 1
   fi

   # Remove zip file
   rm $ZIP_FILE

    # Enter the directory
#    echo "Entering the directory $DIR_NAME..."
#    cd $DIR_NAME
#
#    # Check if the cd was successful
#    if [ $? -ne 0 ]; then
#        echo "Failed to enter the directory $DIR_NAME."
#        exit 1
#    fi

    # Build the microservice framework
    chmod +x *.sh
    source ./check_and_install_maven.sh
    mvn -f $DIR_NAME/pom.xml clean install -D maven.test.skip=true -P prod

    # Move deploy dir and delete micro code
    cp -r $DIR_NAME/docker ./
    cp -r $DIR_NAME/sql ./
    sudo chmod -R 777 ./docker
    sudo chmod -R 777 ./sql

    # web static page
    sudo tar zxvf ./docker/nginx/html.tar.gz -C ./docker/nginx/

    sudo rm -rf $DIR_NAME
}

start_base() {
    echo "Starting base services: mysql, redis, minio"
    docker-compose -f ./docker/docker-compose.yml up -d mysql redis minio
}

start_other() {
    echo "Starting all services"
    docker-compose -f ./docker/docker-compose.yml up -d
}

check_mysql_status() {
    while true ; do
        #command
        sleep 1
        echo "check mysql status..."
        echo "select version();" | mysql -u${dbUserName} -p${dbPwd} -h${dbIP} -P${dbPort}
        if [ $? == 0 ] ; then
            echo "mysql is on"
            break;
        else
            (( ex_count = ${ex_count} + 1 ))
            echo "Waiting mysql to start! ex_count = ${ex_count}."
            if [ ${ex_count} -ge 30 ]; then
                echo "Connect to mysql timeout failed!"
                exit 1
#                break;
            fi
        fi
    done
}

init_database() {
    local dbUserName=$1
    local dbPwd=$2
    local dbIP=$3
    local dbPort=$4

    chmod +x *.sh
    source ./check_and_install_mysqlclient.sh
    check_mysql_status

    echo "Initializing the database"

    init_table "webase-cloud"
    init_table "webase-config"
    init_table "webase-seata"
    init_table "webase-host"
    init_table "webasesign"
    init_table "webasenodemanager3"

    echo "Database initialization complete."
}

init_table() {
    local dbName=$1
    local useCommand="use \`${dbName}\`"
    local createCommand="create database \`${dbName}\` default character set utf8"

    case "$dbName" in
        webase-cloud)
            initTableSql="source ./sql/webase-cloud.sql"
            ;;
        webase-config)
            initTableSql="source ./sql/webase-config.sql"
            ;;
        webase-seata)
            initTableSql="source ./sql/webase-seata.sql"
            ;;
        webase-host)
            initTableSql="source ./sql/webase-host.sql"
            ;;
        webasesign)
            initTableSql=""
            ;;
        webasenodemanager3)
            initTableSql=""
            ;;
        *)
            echo "Unknown database name: $dbName"
            exit 1
            ;;
        esac

    echo "${useCommand}" | mysql -u${dbUserName} -p${dbPwd} -h${dbIP} -P${dbPort}
    if [ $? == 0 ]; then
        echo "database of [${dbName}] already exist, skip init"
    else
        # if return 1(db not exist), create db
        echo "now create database [${dbName}]"
        echo "${createCommand}" | mysql mysql -u${dbUserName} -p${dbPwd} -h${dbIP} -P${dbPort} --default-character-set=utf8
        if [ $? == 0 ]; then
            echo "======== create database success!"
            echo "now create tables"

            # init table
            if [ "$dbName" = "webasenodemanager3" ]; then
                mysql -u${dbUserName} -p${dbPwd} -h${dbIP} -P${dbPort} -D ${dbName} --default-character-set=utf8 -e "source ./sql/webase3/webase-ddl.sql"
                if [ $? == 0 ]; then
                    echo "now init table data"
                    mysql -u${dbUserName} -p${dbPwd} -h${dbIP} -P${dbPort} -D ${dbName} --default-character-set=utf8 -e "source ./sql/webase3/webase-dml.sql"
                    if [ $? == 0 ]; then
                        echo "======== init table data success!"
                    else 
                        echo "======= int table data of [webase-dml.sql] failed!"
                    fi
                else 
                    echo "  ======= create tables of [webase-ddl.sql] failed!"
                fi
            elif [ -n "$initTableSql" ]; then
                mysql -u${dbUserName} -p${dbPwd} -h${dbIP} -P${dbPort} -D ${dbName} --default-character-set=utf8 -e "${initTableSql}"
                if [ $? == 0 ]; then
                    echo "======== init table of $initTableSql data success!"
                else 
                    echo "======= int table data of $initTableSql failed!"
                fi
            else
                echo "initTableSql is empty"
            fi
        else 
            echo "======= create database of [${dbName}] failed!"
        fi
    fi
}

deploy_all() {
    build
    start_base
    init_database "$dbUserName" "$dbPwd" "$dbIP" "$dbPort"
    start_other
    check_service_status
}

check_service_status() {
    log_file="./docker/bcos3/node-mgr/log/WeBASE-Node-Manager.log"
    success_message="main run success"
    container_name="nginx-web"
    container_log_message="webase-gateway:8080 is available"
    max_attempts=60
    attempt=0

    # 循环检查日志文件是否包含成功启动的消息
    while [ $attempt -lt $max_attempts ]; do
        if [ ! -f "$log_file" ]; then
            echo "Log file does not exist."
            sleep 2
            continue
        fi
        if grep -q "$success_message" "$log_file" && docker logs "$container_name" 2>&1 | grep -q "$container_log_message"; then
            echo "WeBASE微服务版本启动成功."
            exit 0
        else
            echo "等待服务启动 尝试次数: $((attempt+1))/$max_attempts"
            attempt=$((attempt+1))
            sleep 2
        fi
    done

    echo "Service did not start successfully after $max_attempts attempts."
    exit 1

}

# 解析 init db 命令的参数
parse_init_db_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u)
                dbUserName="$2"
                shift 2
                ;;
            -p)
                dbPwd="$2"
                shift 2
                ;;
            -h)
                dbIP="$2"
                shift 2
                ;;
            -P)
                dbPort="$2"
                shift 2
                ;;
            *)
                echo "Unknown parameter: $1"
                exit 1
                ;;
        esac
    done

    if [ -z "$dbUserName" ] || [ -z "$dbPwd" ] || [ -z "$dbIP" ] || [ -z "$dbPort" ]; then
        echo "Usage: ./deploy.sh init db -u dbUserName -p dbPwd -h dbIP -P dbPort"
        exit 1
    fi

    init_database "$dbUserName" "$dbPwd" "$dbIP" "$dbPort"
}

parse_init_db_args_for_all() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u)
                dbUserName="$2"
                shift 2
                ;;
            -p)
                dbPwd="$2"
                shift 2
                ;;
            -h)
                dbIP="$2"
                shift 2
                ;;
            -P)
                dbPort="$2"
                shift 2
                ;;
            *)
                echo "Unknown parameter: $1"
                exit 1
                ;;
        esac
    done

    if [ -z "$dbUserName" ] || [ -z "$dbPwd" ] || [ -z "$dbIP" ] || [ -z "$dbPort" ]; then
        echo "Usage: ./deploy.sh all -u dbUserName -p dbPwd -h dbIP -P dbPort"
        exit 1
    fi
}

# Main script logic
case "$1" in
    build)
        build
        ;;
    start)
        case "$2" in
            base)
                start_base
                ;;
            other)
                start_other
                ;;
            *)
                echo "Usage: ./deploy.sh start {base|other}"
                exit 1
                ;;
        esac
        ;;
    init)
        case "$2" in
            db)
                shift 2
                parse_init_db_args "$@"
                ;;
            *)
                echo "Usage: ./deploy.sh init {db}"
                exit 1
                ;;
        esac
        ;;
    all)
        shift
        parse_init_db_args_for_all "$@"
        deploy_all
        ;;
    *)
        echo "Usage: ./deploy.sh {build|start|init|all}"
        exit 1
        ;;
esac