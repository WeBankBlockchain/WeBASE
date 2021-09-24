#!/usr/bin/python3
# encoding: utf-8

import sys
import os
import time
from .utils import *
from .mysql import *

baseDir = getBaseDir()
currentDir = getCurrentBaseDir()
dockerDir = currentDir + "/docker"
serverWaitTime = 5


def installDockerAll():
    configDockerAll()
    checkDbExist()
    startDockerCompose()


def startDockerCompose():
    # check docker-compose
    os.chdir(dockerDir)
    doCmd("docker-compose up -d") 
    print ("start docker container success!")

def stopDockerCompose():
    os.chdir(dockerDir)
    doCmd("docker-compose down")
    # restart by [docker-compose stop, docker-compose start, docker-compose restart]

def statusFisco():
    # check docker-compose
    doCmd("docker ps | grep fiscobcos")

def statusWebase():
    # check docker-compose
    doCmd("docker-compose ps")


def pullDockerComposeImages():
    print("use [vi /etc/docker/daemon.json] to alter your docker image repository source")
    # check docker deamon.json
    timeout=60
    info = "60"      
    if sys.version_info.major == 2:
        info =  raw_input("Exec [docker pull] command to get images, please type in timeout seconds, example: [30/60/120]: ")
    else:
        info = input("Exec [docker pull] command to get images, please type in timeout seconds, example: [30/60/120]: ")
    if info.isdigit():
        timeout=int(info)
    else: 
        raise Exception("input [timeout] number of {} not validate, must be digit number!".format(info))
    print ("start pull docker images of fiscobcos, mysql and WeBASE...")
    # pull fisco bcos node
    # version ex: 2.8.0, required add v as v2.8.0
    node_version = getCommProperties("fisco.version")
    fisco_repo = "fiscoorg/fiscobcos:v" + node_version 
    if not checkDockerImageExist(fisco_repo):
        print("now pull docker image of {}".format(fisco_repo))
        result = doCmdTimeout("docker pull {}".format(fisco_repo), timeout)
        # if code is not zero, throw exception
        # if code is zero, success or timeout
        if result["status"] == 0 and result["output"] == "timeout":
            print("[ERROR] pull image of [{}] timeout, please manually pull".format(fisco_repo))
        else:
            print("pull docker image of {} success".format(fisco_repo))
            
    # pull mysql
    docker_mysql = int(getCommProperties("docker.mysql"))
    if docker_mysql == 1:
        mysql_repo_name = "mysql:5.6"    
        if not checkDockerImageExist(mysql_repo_name):
            print("now pull docker image of {}".format(mysql_repo_name))
            result = doCmdTimeout("docker pull {}".format(mysql_repo_name), timeout)
            # if code is not zero, throw exception
            # if code is zero, success or timeout
            if result["status"] == 0 and result["output"] == "timeout":
                print("[ERROR] pull image of [{}] timeout, please manually pull".format(mysql_repo_name))
            else:
                print("pull docker image of {} success".format(mysql_repo_name))
    else:
        print("not using docker mysql, skip pull mysql:5.6")

    front_version = getCommProperties("webase.front.version")
    mgr_version = getCommProperties("webase.mgr.version")
    sign_version = getCommProperties("webase.sign.version")
    web_version = getCommProperties("webase.web.version")
    
    pullSingleImage("webase-front", front_version, timeout)
    pullSingleImage("webase-node-mgr", mgr_version, timeout)
    pullSingleImage("webase-sign", sign_version, timeout)
    pullSingleImage("webase-web", web_version, timeout)
    print ("Successfully pull!")

# image_name: webase-front
# image_ver: v1.5.3
def pullSingleImage(image_name,image_ver,timeout):
    # ex: webasepro/webase-front:v1.5.3
    repo_with_ver = "webasepro/" + image_name + ":" + image_ver
    if not checkDockerImageExist(repo_with_ver):
        print("now pull docker image of {}".format(repo_with_ver))
        result = doCmdTimeout("docker pull {}".format(repo_with_ver), timeout)
        # if code is not zero, throw exception
        # if code is zero, success or timeout
        if result["status"] == 0 and result["output"] == "timeout":
            print("[ERROR] pull image of [{}] timeout, please manually pull".format(repo_with_ver))
        else:
            print("pull docker image of {} success".format(repo_with_ver))


def configDockerAll():
    # in deploy.py dir
    os.chdir(currentDir)
    doCmdIgnoreException("chmod u+x ./docker/script/*.sh")
    doCmdIgnoreException("dos2unix ./docker/script/*.sh")
    # init default template yaml
    if not os.path.exists(dockerDir + "/docker-compose-temp.yaml"):
        doCmd('cp -f {}/docker-compose.yaml {}/docker-compose-temp.yaml'.format(dockerDir, dockerDir))
    else:
        doCmd('cp -f {}/docker-compose-temp.yaml {}/docker-compose.yaml'.format(dockerDir, dockerDir))

    # config nginx.conf
    configWeb()
    # update yaml of each service
    updateYamlMysql()
    updateYamlSign()
    updateYamlFront()
    updateYamlMgr()
    updateYamlWeb()
    
# run after config yaml
def checkDbExist():
    # if docker mysql
    # check mysql file, then docker-compose up mysql
    # use pymysql to drop db
    docker_mysql = int(getCommProperties("docker.mysql"))
    if docker_mysql == 1:
        # check mysql files
        print ("check database if exist in [docker mysql]")
        if os.path.exists("{}/mysql/data/webasesign".format(currentDir)) or os.path.exists("{}/mysql/data/webasenodemanager".format(currentDir)):
            # start
            doCmd("docker-compose -f docker/docker-compose.yaml up -d mysql")
            print ("checking...")
            timeTemp = 0
            while timeTemp < serverWaitTime :
                print(".", end='')
                sys.stdout.flush()
                time.sleep(1)
                timeTemp = timeTemp + 1
            # sleep until mysql is on
            dropDockerDb("webasesign")
            dropDockerDb("webasenodemanager")
            # end
            print ("ending check [docker mysql]...")
            doCmd("docker-compose -f docker/docker-compose.yaml stop mysql") 
    else:
        print ("check database if exist in mysql...")
        checkAndDropSignDb()
        checkAndDropMgrDb()
    print ("end check mysql databases")


###### mysql config ######
# update mysql/node-mgr/sign configuration
def updateYamlMysql():
    print ("update mysql configuration in yaml")
    # set root's password
    docker_mysql = int(getCommProperties("docker.mysql"))
    if docker_mysql == 1:
        print ("using [mysql in docker] mode")    
        docker_mysql_port = getCommProperties("docker.mysql.port")
        docker_mysql_pwd = getCommProperties("docker.mysql.password")
        mysql_data_dir = currentDir + "/mysql/data"
        # update mysql docker
        doCmd('sed -i "s:23306:{}:g" {}/docker-compose.yaml'.format(docker_mysql_port, dockerDir))
        doCmd('sed -i "s:123456:{}:g" {}/docker-compose.yaml'.format(docker_mysql_pwd, dockerDir))
        doCmd('sed -i "s:/webase-deploy/mysql/data:{}:g" {}/docker-compose.yaml'.format(mysql_data_dir, dockerDir))
        # mgr docker
        doCmd('sed -i "s:mgrDbIp:127.0.0.1:g" {}/docker-compose.yaml'.format(dockerDir))
        doCmd('sed -i "s:mgrDbPort:{}:g" {}/docker-compose.yaml'.format(docker_mysql_port, dockerDir))
        doCmd('sed -i "s:mgrDefaultAccount:root:g" {}/docker-compose.yaml'.format(dockerDir))
        doCmd('sed -i "s:mgrDefaultPassword:{}:g" {}/docker-compose.yaml'.format(docker_mysql_pwd, dockerDir))
        # sign docker
        doCmd('sed -i "s:signDbIp:127.0.0.1:g" {}/docker-compose.yaml'.format(dockerDir))
        doCmd('sed -i "s:signDbPort:{}:g" {}/docker-compose.yaml'.format(docker_mysql_port, dockerDir))
        doCmd('sed -i "s:signDefaultAccount:root:g" {}/docker-compose.yaml'.format(dockerDir))
        doCmd('sed -i "s:signDefaultPassword:{}:g" {}/docker-compose.yaml'.format(docker_mysql_pwd, dockerDir))
    else:
        print ("using [mysql in host] mode")    
        ## not use mysql docker, read configured mysql of node-mgr and sign
        # disable mysql docker
        doCmd('sed -i "s:# entrypoint:entrypoint:g" {}/docker-compose.yaml'.format(dockerDir))
    
        ### set mgr ip port
        # checkMgrDb
        mgr_mysql_ip = getCommProperties("mysql.ip")
        if mgr_mysql_ip == 'localhost':
            mgr_mysql_ip = '127.0.0.1'
        mgr_mysql_port = getCommProperties("mysql.port")
        mgr_mysql_user = getCommProperties("mysql.user")
        mgr_mysql_password = getCommProperties("mysql.password")
        mgr_mysql_database = getCommProperties("mysql.database")
        doCmd('sed -i "s:webasenodemanager:{}:g" {}/docker-compose.yaml'.format(mgr_mysql_database, dockerDir))
        doCmd('sed -i "s:mgrDbIp:{}:g" {}/docker-compose.yaml'.format(mgr_mysql_ip, dockerDir))
        doCmd('sed -i "s:mgrDbPort:{}:g" {}/docker-compose.yaml'.format(mgr_mysql_port, dockerDir))
        doCmd('sed -i "s:mgrDefaultAccount:{}:g" {}/docker-compose.yaml'.format(mgr_mysql_user, dockerDir))
        doCmd('sed -i "s:mgrDefaultPassword:{}:g" {}/docker-compose.yaml'.format(mgr_mysql_password, dockerDir))

        sign_mysql_ip = getCommProperties("sign.mysql.ip")
        if sign_mysql_ip == 'localhost':
            sign_mysql_ip = '127.0.0.1'        
        sign_mysql_port = getCommProperties("sign.mysql.port")
        sign_mysql_user = getCommProperties("sign.mysql.user")
        sign_mysql_password = getCommProperties("sign.mysql.password")
        sign_mysql_database = getCommProperties("sign.mysql.database")
        doCmd('sed -i "s:webasesign:{}:g" {}/docker-compose.yaml'.format(sign_mysql_database, dockerDir))
        doCmd('sed -i "s:signDbIp:{}:g" {}/docker-compose.yaml'.format(sign_mysql_ip, dockerDir))
        doCmd('sed -i "s:signDbPort:{}:g" {}/docker-compose.yaml'.format(sign_mysql_port, dockerDir))
        doCmd('sed -i "s:signDefaultAccount:{}:g" {}/docker-compose.yaml'.format(sign_mysql_user, dockerDir))
        doCmd('sed -i "s:signDefaultPassword:{}:g" {}/docker-compose.yaml'.format(sign_mysql_password, dockerDir))
   
    print ("end mysql configuration in yaml")


def updateYamlFront():
    print ("update webase-front configuration in yaml")
    front_dir = currentDir + "/webase-front"
    front_version = getCommProperties("webase.front.version")
    front_port = getCommProperties("front.port")
    channel_ip = getCommProperties("node.listenIp")
    channel_port = getCommProperties("node.channelPort")
    front_db = getCommProperties("front.h2.name")
    sign_port = getCommProperties("sign.port")

    # config node path and sdk path
    if_exist_fisco = getCommProperties("if.exist.fisco")
    fisco_dir = getCommProperties("fisco.dir")
    node_relative_dir = getCommProperties("node.dir")
    node_dir = fisco_dir + "/" + node_relative_dir
    if if_exist_fisco == "no":
        fisco_dir = currentDir + "/nodes/127.0.0.1"
        node_dir = currentDir + "/nodes/127.0.0.1/node0"
    sdk_dir = fisco_dir + "/sdk"

    doCmd('sed -i "s/5002/{}/g" {}/docker-compose.yaml'.format(front_port, dockerDir))
    doCmd('sed -i "s/webasefront/{}/g" {}/docker-compose.yaml'.format(front_db, dockerDir))
    doCmd('sed -i "s/webase-front:v0.0.2/webase-front:{}/g" {}/docker-compose.yaml'.format(front_version, dockerDir))
    doCmd('sed -i "s/sdkIp/{}/g" {}/docker-compose.yaml'.format(channel_ip, dockerDir))
    doCmd('sed -i "s/sdkChannelPort/{}/g" {}/docker-compose.yaml'.format(channel_port, dockerDir))
    doCmd('sed -i "s/signIpPort/127.0.0.1:{}/g" {}/docker-compose.yaml'.format(sign_port, dockerDir))
    doCmd('sed -i "s:/webase-deploy/webase-front:{}:g" {}/docker-compose.yaml'.format(front_dir, dockerDir))
    # doCmd('sed -i "s:frontNodePath:{}:g" {}/docker-compose.yaml'.format(node_dir, dockerDir))
    doCmd('sed -i "s:/webase-deploy/nodes/127.0.0.1/sdk:{}:g" {}/docker-compose.yaml'.format(sdk_dir, dockerDir))
    print ("end webase-front configuration in yaml")


def updateYamlMgr():
    print ("update webase-node-mgr configuration in yaml")
    mgr_version = getCommProperties("webase.mgr.version")
    mgr_port = getCommProperties("mgr.port")
    encrypt_type = getCommProperties("encrypt.type")
    mgr_dir = currentDir + "/webase-node-mgr"
    doCmd('sed -i "s:/webase-deploy/webase-node-mgr:{}:g" {}/docker-compose.yaml'.format(mgr_dir, dockerDir))
    doCmd('sed -i "s/webase-node-mgr:v0.0.2/webase-node-mgr:{}/g" {}/docker-compose.yaml'.format(mgr_version, dockerDir))
    doCmd('sed -i "s/5001/{}/g" {}/docker-compose.yaml'.format(mgr_port, dockerDir))
    doCmd('sed -i "s/mgrEncryptType/{}/g" {}/docker-compose.yaml'.format(encrypt_type, dockerDir))
    print ("end webase-node-mgr configuration in yaml")


def updateYamlSign():
    print ("update webase-sign configuration in yaml")
    sign_version = getCommProperties("webase.sign.version")
    sign_port = getCommProperties("sign.port")
    sign_dir = currentDir + "/webase-sign"
    doCmd('sed -i "s:/webase-deploy/webase-sign:{}:g" {}/docker-compose.yaml'.format(sign_dir, dockerDir))
    doCmd('sed -i "s/webase-sign:v0.0.2/webase-sign:{}/g" {}/docker-compose.yaml'.format(sign_version, dockerDir))
    doCmd('sed -i "s/5004/{}/g" {}/docker-compose.yaml'.format(sign_port, dockerDir))
    print ("end webase-sign configuration in yaml")
    


def updateYamlWeb():
    print ("update webase-web configuration in yaml")
    web_version = getCommProperties("webase.web.version")
    web_port = getCommProperties("web.port")
    web_dir = currentDir + "/webase-web"
    doCmd('sed -i "s:/webase-deploy/webase-web:{}:g" {}/docker-compose.yaml'.format(web_dir, dockerDir))
    doCmd('sed -i "s/webase-web:v0.0.2/webase-web:{}/g" {}/docker-compose.yaml'.format(web_version, dockerDir))
    doCmd('sed -i "s/5000/{}/g" {}/docker-compose.yaml'.format(web_port, dockerDir))
    print ("end webase-web configuration in yaml")
    

###### webase-web config ######
def configWeb():
    print ("configure nginx.conf file of webase-web")
    # dir of webase-web
    web_conf_dir = currentDir + "/comm"
    web_dir = currentDir + "/webase-web"
    web_log_dir = web_dir + "/log"

    # copy nginx-docker.conf
    doCmd('mkdir -p {}'.format(web_dir))
    if not os.path.exists(web_dir + "/nginx-docker.conf"):
        doCmd('cp -f {}/nginx.conf {}/nginx-docker.conf'.format(web_conf_dir, web_dir))

    # get properties
    web_port = getCommProperties("web.port")
    mgr_port = getCommProperties("mgr.port")
    # doCmd('mkdir -p {}'.format(web_log_dir))
    doCmd('sed -i "s/5000/{}/g" {}/nginx-docker.conf'.format(web_port, web_dir))
    doCmd('sed -i "s/server 127.0.0.1:5001/server 127.0.0.1:{}/g" {}/nginx-docker.conf'.format(mgr_port, web_dir))
    ## constant dir in docker container
    doCmd('sed -i "s:log_path:/dist/log:g" {}/nginx-docker.conf'.format(web_dir))
    doCmd('sed -i "s:pid pid_file:# pid pid_file:g" {}/nginx-docker.conf'.format(web_dir))
    doCmd('sed -i "s:web_page_url:/data/webase-web/dist:g" {}/nginx-docker.conf'.format(web_dir))
    ## todo docker mode not support h5 mobile version of webase-web
    # set mobile phone phone_page_url globally
    doCmd('sed -i "s:phone_page_url:/data/webase-web/dist:g" {}/nginx-docker.conf'.format(web_dir))
    print ("end nginx configuration")


## check mysql in docker exsit and drop
def dropDockerDb(db2reset):
    log.info("dropDockerDb {}".format(db2reset))
    # get properties
    mysql_ip = "127.0.0.1"
    mysql_user = "root"
    mysql_port = int(getCommProperties("docker.mysql.port"))
    mysql_password_raw = getCommProperties("docker.mysql.password")
    mysql_password = parse.unquote_plus(mysql_password_raw)  
    try:
        # connect
        conn = mdb.connect(host=mysql_ip, port=mysql_port, user=mysql_user, passwd=mysql_password, charset='utf8')
        conn.autocommit(1)
        cursor = conn.cursor()
        
        # check db
        result = cursor.execute('show databases like "%s"' %db2reset)
        drop_db = 'DROP DATABASE IF EXISTS {}'.format(db2reset)
        if result == 1:
            info = "n"
            if sys.version_info.major == 2:
                info = raw_input("database of [{}] already exists. Do you want drop and recreate it?[y/n]:".format(db2reset))
            else:
                info = input("database of [{}] already exists. Do you want drop and recreate it?[y/n]:".format(db2reset))
            if info == "y" or info == "Y":
                log.info(drop_db)
                cursor.execute(drop_db)
        cursor.close()
        conn.close()
    except:
        import traceback
        log.info(" mysql except {}".format(traceback.format_exc()))
        traceback.print_exc()
        sys.exit(0)
    

def checkAndDropMgrDb():
    # get properties
    mysql_ip = getCommProperties("mysql.ip")
    mysql_port = int(getCommProperties("mysql.port"))
    mysql_user = getCommProperties("mysql.user")
    mysql_password_raw = getCommProperties("mysql.password")
    mysql_password = parse.unquote_plus(mysql_password_raw)      
    mysql_database = getCommProperties("mysql.database")

    try:
        # connect
        conn = mdb.connect(host=mysql_ip, port=mysql_port, user=mysql_user, passwd=mysql_password, charset='utf8')
        conn.autocommit(1)
        cursor = conn.cursor()
        
        # check db
        result = cursor.execute('show databases like "%s"' %mysql_database)
        drop_db = 'DROP DATABASE IF EXISTS {}'.format(mysql_database)
        if result == 1:
            info = "n"
            if sys.version_info.major == 2:
                info = raw_input("WeBASE-Node-Manager database {} already exists. Do you want drop and re-initialize it?[y/n]:".format(mysql_database))
            else:
                info = input("WeBASE-Node-Manager database {} already exists. Do you want drop and re-initialize it?[y/n]:".format(mysql_database))
            if info == "y" or info == "Y":
                log.info(drop_db)
                cursor.execute(drop_db)
        cursor.close()
        conn.close()
    except:
        import traceback
        log.info(" mysql except {}".format(traceback.format_exc()))
        traceback.print_exc()
        sys.exit(0)

def checkAndDropSignDb():
    # get properties
    mysql_ip = getCommProperties("sign.mysql.ip")
    mysql_port = int(getCommProperties("sign.mysql.port"))
    mysql_user = getCommProperties("sign.mysql.user")
    mysql_password_raw = getCommProperties("sign.mysql.password")
    mysql_password = parse.unquote_plus(mysql_password_raw)  
    mysql_database = getCommProperties("sign.mysql.database")
    try:
        # connect
        conn = mdb.connect(host=mysql_ip, port=mysql_port, user=mysql_user, passwd=mysql_password, charset='utf8')
        conn.autocommit(1)
        cursor = conn.cursor()
        
        # check db
        result = cursor.execute('show databases like "%s"' %mysql_database)
        drop_db = 'DROP DATABASE IF EXISTS {}'.format(mysql_database)
        if result == 1:
            info = "n"
            if sys.version_info.major == 2:
                info = raw_input("WeBASE-Sign database {} already exists. Do you want drop and recreate it?[y/n]:".format(mysql_database))
            else:
                info = input("WeBASE-Sign database {} already exists. Do you want drop and recreate it?[y/n]:".format(mysql_database))
            if info == "y" or info == "Y":
                log.info(drop_db)
                cursor.execute(drop_db)
        cursor.close()
        conn.close()
    except:
        import traceback
        log.info(" mysql except {}".format(traceback.format_exc()))
        traceback.print_exc()
        sys.exit(0)
    
