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

# 要求docker无需sudo

def installDockerAll():
    configDockerAll()
    # if timeout, use cdn
    pullDockerImages()
    startDockerCompose()

def pullDockerImages():
    # check docker-compose
    os.chdir(dockerDir)
    doCmd("docker-compose pull --parallel")
    
def startDockerCompose():
    # check docker-compose
    os.chdir(dockerDir)
    doCmd("docker-compose up -d")
    # docker-compose down

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

def configDockerAll():
    # in deploy.py dir
    os.chdir(currentDir)
    doCmdIgnoreException("chmod u+x ./docker/script/*.sh")
    doCmdIgnoreException("dos2unix ./docker/script/*.sh")
    if not os.path.exists(dockerDir + "/docker-compose-temp.yaml"):
        doCmd('cp -f {}/docker-compose.yaml {}/docker-compose-temp.yaml'.format(dockerDir, dockerDir))

    # config nginx.conf
    configWeb()
    # update yaml of each service
    updateYamlMysql()
    updateYamlSign()
    updateYamlFront()
    updateYamlMgr()
    updateYamlWeb()
    

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
    doCmd('sed -i "s:frontNodePath:{}:g" {}/docker-compose.yaml'.format(node_dir, dockerDir))
    doCmd('sed -i "s:/webase-deploy/nodes/127.0.0.1/sdk:{}:g" {}/docker-compose.yaml'.format(sdk_dir, dockerDir))
    print ("end webase-front configuration in yaml")


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
        # print("!!Important!! you should type in mysql's configuration in ./docker/docker-compose.yaml of webase-node-mgr and webase-sign")
    
        ### set mgr ip port
        # checkMgrDb
        mgr_mysql_ip = getCommProperties("mysql.ip")
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

