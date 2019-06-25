#!/usr/bin/python
# encoding: utf-8

import sys
import os
from utils import *
from mysql import *

baseDir = getBaseDir()
currentDir = getCurrentBaseDir()

def do():
    print "=====================    deploy   start... ====================="
    startNode()
    startWeb()
    startMgr()
    startFront()
    print "=====================    deploy   end...   ====================="
    print "=====================    version  V1.0.0   ====================="
    return
    
def end():
    stopNode()
    stopWeb()
    stopMgr()
    stopFront()
    return

def startNode():
    print "============== node start... =============="
    fisco_version = getCommProperties("fisco.version")
    nodes = getCommProperties("node.counts")
    node_p2pPort = int(getCommProperties("node.p2pPort"))
    node_channelPort = int(getCommProperties("node.channelPort"))
    node_rpcPort = int(getCommProperties("node.rpcPort"))
    
    # init configure file
    if not os.path.exists(currentDir + "/nodetemp"):
        doCmd('cp -f nodeconf nodetemp')
    else:
        doCmd('cp -f nodetemp nodeconf')
        
    node_counts = 2
    if nodes is not "nodeCounts":
        node_counts = int(nodes)
    doCmd('sed -i "s/nodeCounts/{}/g" nodeconf'.format(node_counts))
    
    if not os.path.exists("{}/nodes".format(currentDir)):
        doCmdIgnoreException("chmod u+x *.sh")
        doCmdIgnoreException("dos2unix *.sh")
        result_build = doCmd("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
        if result_build["status"] == 0:
            if_build = 'completed' in result_build["output"]
            if not if_build:
                print "======= node build fail! ======="
                sys.exit(0)
        else:
            print "======= node build fail! ======="
            sys.exit(0)
    else:
        info = raw_input("节点目录nodes已经存在。是否重新安装？[y/n]:")
        if info == "y" or info == "Y":
            doCmdIgnoreException("bash nodes/127.0.0.1/stop_all.sh")
            doCmd("rm -rf nodes")
            doCmdIgnoreException("chmod u+x *.sh")
            doCmdIgnoreException("dos2unix *.sh")
            result_build = doCmd("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
            if result_build["status"] == 0:
                if_build = 'completed' in result_build["output"]
                if not if_build:
                    print "======= node build fail! ======="
                    sys.exit(0)
            else:
                print "======= node build fail! ======="
                sys.exit(0)
    
    node_dir = currentDir + "/nodes/127.0.0.1"
    os.chdir(node_dir)
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    os.system("bash start_all.sh")
    print "============== node end...   =============="
    return
    
def stopNode():
    if not os.path.exists("{}/nodes".format(currentDir)):
        print "======= nodes is not exists! ======="
        sys.exit(0)
    
    node_dir = currentDir + "/nodes/127.0.0.1"
    os.chdir(node_dir)
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    os.system("bash stop_all.sh")
    return
    
def changeWebConfig():
    # get properties
    deploy_ip = "127.0.0.1"
    web_port = getCommProperties("web.port")
    mgr_port = getCommProperties("mgr.port")

    # init configure file
    web_conf_dir = currentDir + "/comm"
    if not os.path.exists(web_conf_dir + "/temp.conf"):
        doCmd('cp -f {}/nginx.conf {}/temp.conf'.format(web_conf_dir, web_conf_dir))
    else:
        doCmd('cp -f {}/temp.conf {}/nginx.conf'.format(web_conf_dir, web_conf_dir))

    # change web config
    web_dir = currentDir + "/webase-web"
    web_log_dir = web_dir + "/log"
    doCmd('mkdir -p {}'.format(web_log_dir))
    doCmd('sed -i "s/127.0.0.1/{}/g" {}/comm/nginx.conf'.format(deploy_ip, currentDir))
    doCmd('sed -i "s/3002/{}/g" {}/comm/nginx.conf'.format(web_port, currentDir))
    doCmd('sed -i "s/10.0.0.1:8083/{}:{}/g" {}/comm/nginx.conf'.format(deploy_ip, mgr_port, currentDir))
    doCmd('sed -i "s:log_path:{}:g" {}/comm/nginx.conf'.format(web_log_dir, currentDir))
    doCmd('sed -i "s:web_page_url:{}:g" {}/comm/nginx.conf'.format(web_dir, currentDir))

    return

def startWeb():
    print "==============  web start... =============="
    os.chdir(currentDir)
    pullSourceExtract("web.package.url","webase-web")
    changeWebConfig()
    
    nginx_config_dir = currentDir + "/comm/nginx.conf"
    res = doCmd("which nginx")
    if res["status"] == 0:
        res2 = doCmd("sudo " + res["output"] + " -c " + nginx_config_dir)
        if res2["status"] == 0:
            print "=======  web  start success! ======="
        else:
            print "=======  web  start fail!    ======="
            sys.exit(0)
    else:
        print "=======  web  start fail!    ======="
        sys.exit(0)
    print "==============  web end...   =============="
    return
    
def stopWeb():
    if os.path.exists("/run/nginx-webase-web.pid"):
        fin = open('/run/nginx-webase-web.pid', 'r')
        pid = fin.read()
        cmd = "sudo kill -QUIT {}".format(pid)
        os.system(cmd)
        doCmdIgnoreException("sudo rm -rf /run/nginx-webase-web.pid")
        print "=======  web  stop success! ======="
    else:
        print "=======  web  is not running! ======="
    return

def changeMgrConfig():
    # get properties
    mgr_port = getCommProperties("mgr.port")
    mysql_ip = getCommProperties("mysql.ip")
    mysql_port = getCommProperties("mysql.port")
    mysql_user = getCommProperties("mysql.user")
    mysql_password = getCommProperties("mysql.password")
    mysql_database = getCommProperties("mysql.database")
        
    # init file
    server_dir = currentDir + "/webase-node-mgr"
    script_dir = server_dir + "/script"
    conf_dir = server_dir + "/conf"
    if not os.path.exists(script_dir + "/temp.sh"):
        doCmd('cp -f {}/webase.sh {}/temp.sh'.format(script_dir, script_dir))
    else:
        doCmd('cp -f {}/temp.sh {}/webase.sh'.format(script_dir, script_dir))
    if not os.path.exists(conf_dir + "/temp.yml"):
        doCmd('cp -f {}/application.yml {}/temp.yml'.format(conf_dir, conf_dir))
    else:
        doCmd('cp -f {}/temp.yml {}/application.yml'.format(conf_dir, conf_dir))
        
    # change script config
    doCmd('sed -i "s/defaultAccount/{}/g" {}/webase.sh'.format(mysql_user, script_dir))
    doCmd('sed -i "s/defaultPassword/{}/g" {}/webase.sh'.format(mysql_password, script_dir))
    doCmd('sed -i "s/fisco-bcos-data/{}/g" {}/webase.sh'.format(mysql_database, script_dir))
    
    # change server config
    doCmd('sed -i "s/8080/{}/g" {}/application.yml'.format(mgr_port, conf_dir))
    doCmd('sed -i "s/127.0.0.1/{}/g" {}/application.yml'.format(mysql_ip, conf_dir))
    doCmd('sed -i "s/3306/{}/g" {}/application.yml'.format(mysql_port, conf_dir))
    doCmd('sed -i "s/defaultAccount/{}/g" {}/application.yml'.format(mysql_user, conf_dir))
    doCmd('sed -i "s/defaultPassword/{}/g" {}/application.yml'.format(mysql_password, conf_dir))
    doCmd('sed -i "s/fisco-bcos-data/{}/g" {}/application.yml'.format(mysql_database, conf_dir))

    return
    
def startMgr():
    print "==============  mgr start... =============="
    os.chdir(currentDir)
    pullSourceExtract("mgr.package.url","webase-node-mgr")
    changeMgrConfig()
    dbConnect()
    
    mysql_ip = getCommProperties("mysql.ip")
    mysql_port = getCommProperties("mysql.port")
    server_dir = currentDir + "/webase-node-mgr"
    script_dir = server_dir + "/script"
    
    info = raw_input("是否初始化数据(首次部署或重建库需执行)？[y/n]:")
    if info == "y" or info == "Y":
        os.chdir(script_dir)
        doCmdIgnoreException("chmod u+x *.sh")
        doCmdIgnoreException("dos2unix *.sh")
        dbResult = doCmd('bash webase.sh {} {}'.format(mysql_ip, mysql_port))
        if dbResult["status"] == 0:
            if_success = 'success' in dbResult["output"]
            if if_success:
                print "======= script init success! ======="
            else:
                print "======= script init fail! ======="
                print dbResult["output"]
                sys.exit(0)
        else:
            print "======= script init fail! ======="
            sys.exit(0)
    
    os.chdir(server_dir)
    doCmdIgnoreException("source /etc/profile")
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    result = doCmd("bash start.sh")
    if result["status"] == 0:
        if_started = 'started' in result["output"]
        if if_started:
            info = raw_input("mgr进程已经存在，是否kill进程强制安装？[y/n]:")
            if info == "y" or info == "Y":
                doCmd("bash stop.sh")
                result_start = doCmd("bash start.sh")
                if result_start["status"] == 0:
                    if_success = 'Success' in result_start["output"]
                    if if_success:
                        print "=======  mgr  start success! ======="
                    else:
                        print "======= mgr start fail!  ======="
                        sys.exit(0)
                else:
                    print "======= mgr start fail!  ======="
                    sys.exit(0)
                return
            else:
                sys.exit(0)
        if_success = 'Success' in result["output"]
        if if_success:
            print "=======  mgr  start success! ======="
        else:
            print "======= mgr start fail!  ======="
            sys.exit(0)
    else:
        print "======= mgr start fail!  ======="
        sys.exit(0)
    print "==============  mgr end...   =============="
    return
        
def stopMgr():
    server_dir = currentDir + "/webase-node-mgr"
    os.chdir(server_dir)
    doCmdIgnoreException("source /etc/profile")
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    result = doCmd("bash stop.sh")
    if result["status"] == 0:
        if_success = 'Success' in result["output"]
        if if_success:
            print "=======  mgr  stop success! ======="
        else:
            print "=======  mgr  is not running! ======="
    else:
        print "=======  mgr  stop fail! ======="
    return
        
def changeFrontConfig():
    # get properties
    deploy_ip = "127.0.0.1"
    mgr_port = getCommProperties("mgr.port")
    frontPort = getCommProperties("front.port")
    nodeChannelPort = getCommProperties("node.channelPort")
    frontDb = getCommProperties("front.h2.db")
    monitorDisk = getCommProperties("monitorDisk")

    # init file
    server_dir = currentDir + "/webase-front/conf"
    db_dir = currentDir + "/h2"
    doCmdIgnoreException("mkdir -p {}".format(db_dir))
    if not os.path.exists(server_dir + "/temp.yml"):
        doCmd('cp -f {}/application.yml {}/temp.yml'.format(server_dir, server_dir))
    else:
        doCmd('cp -f {}/temp.yml {}/application.yml'.format(server_dir, server_dir))
        
    # change server config
    doCmd('sed -i "s/20200/{}/g" {}/application.yml'.format(nodeChannelPort, server_dir))
    doCmd('sed -i "s/8081/{}/g" {}/application.yml'.format(frontPort, server_dir))
    doCmd('sed -i "s/127.0.0.1:8080/{}:{}/g" {}/application.yml'.format(deploy_ip, mgr_port, server_dir))
    doCmd('sed -i "s%h2Path%{}%g" {}/application.yml'.format(db_dir, server_dir))
    doCmd('sed -i "s%front_db%{}%g" {}/application.yml'.format(frontDb, server_dir))
    doCmd('sed -i "s%/data%{}%g" {}/application.yml'.format(monitorDisk, server_dir))

    return
    
def startFront():
    print "==============  front start... =============="
    os.chdir(currentDir)
    pullSourceExtract("front.package.url","webase-front")
    changeFrontConfig()
    
    # check front db
    frontDb = getCommProperties("front.h2.db")
    db_dir = currentDir+"/h2"
    res_file = checkFileName(db_dir,frontDb)
    if res_file:
        info = raw_input("front数据库{}已经存在，是否删除重建？[y/n]:".format(frontDb))
        if info == "y" or info == "Y":
            doCmdIgnoreException("rm -rf {}/{}.*".format(db_dir,frontDb))
    
    nodeDir = currentDir + "/nodes/127.0.0.1/sdk"
    server_dir = currentDir + "/webase-front"
    os.chdir(server_dir)
    # copy crt
    copyFiles(nodeDir, server_dir + "/conf")
    
    doCmdIgnoreException("source /etc/profile")
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    result = doCmd("bash start.sh")
    if result["status"] == 0:
        if_started = 'started' in result["output"]
        if if_started:
            info = raw_input("front进程已经存在，是否kill进程强制安装？[y/n]:")
            if info == "y" or info == "Y":
                doCmd("bash stop.sh")
                result_start = doCmd("sh start.sh")
                if result_start["status"] == 0:
                    if_success = 'Success' in result_start["output"]
                    if if_success:
                        print "======= front start success! ======="
                    else:
                        print "======= front start fail!    ======="
                        sys.exit(0)
                else:
                    print "======= front start fail!    ======="
                    sys.exit(0)
                return
            else:
                sys.exit(0)
        if_success = 'Success' in result["output"]
        if if_success:
            print "======= front start success! ======="
        else:
            print "======= front start fail!    ======="
            sys.exit(0)
    else:
        print "======= front start fail!    ======="
        sys.exit(0)
    print "==============  front end...   =============="
    return
        
def stopFront():
    server_dir = currentDir + "/webase-front"
    os.chdir(server_dir)
    doCmdIgnoreException("source /etc/profile")
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    result = doCmd("bash stop.sh")
    if result["status"] == 0:
        if_success = 'Success' in result["output"]
        if if_success:
            print "======= front stop success! ======="
        else:
            print "======= front is not running! ======="
    else:
        print "======= front stop fail! ======="
    return
