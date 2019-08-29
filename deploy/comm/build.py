#!/usr/bin/python3
# encoding: utf-8

import sys
import os
from .utils import *
from .mysql import dbConnect

baseDir = getBaseDir()
currentDir = getCurrentBaseDir()

def do():
    print ("=====================    deploy   start... =====================")
    installNode()
    installWeb()
    installManager()
    installFront()
    print ("=====================    deploy   end...   =====================")
    os.chdir(currentDir)
    version = getCommProperties("webase.version")
    print ("=====================    version  {}   =====================".format(version))
    print ("================================================================")
    return
    
def end():
    stopNode()
    stopWeb()
    stopManager()
    stopFront()
    return

def installNode():
    if_exist_fisco = getCommProperties("if.exist.fisco")
    node_p2pPort = int(getCommProperties("node.p2pPort"))
    node_channelPort = int(getCommProperties("node.channelPort"))
    node_rpcPort = int(getCommProperties("node.rpcPort"))
    fisco_version = getCommProperties("fisco.version")
    node_counts = getCommProperties("node.counts")
    
    if if_exist_fisco == "no":
        print ("================================================================")
        print ("==============      FISCO-BCOS     install... ==============")
        # init configure file
        if not os.path.exists(currentDir + "/nodetemp"):
            doCmd('cp -f nodeconf nodetemp')
        else:
            doCmd('cp -f nodetemp nodeconf')
            
        node_nums = 2
        if node_counts != "nodeCounts":
            node_nums = int(node_counts)
        doCmd('sed -i "s/nodeCounts/{}/g" nodeconf'.format(node_nums))
        
        if not os.path.exists("{}/nodes".format(currentDir)):
            doCmdIgnoreException("chmod u+x *.sh")
            doCmdIgnoreException("dos2unix *.sh")
            os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
        else:
            info = "n"
            if sys.version_info.major == 2:
                info = raw_input("FISCO-BCOS节点目录nodes已经存在。是否重新安装？[y/n]:")
            else:
                info = input("FISCO-BCOS节点目录nodes已经存在。是否重新安装？[y/n]:")
            if info == "y" or info == "Y":
                doCmdIgnoreException("bash nodes/127.0.0.1/stop_all.sh")
                doCmd("rm -rf nodes")
                doCmdIgnoreException("chmod u+x *.sh")
                doCmdIgnoreException("dos2unix *.sh")
                os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
    startNode()
    
def startNode():
    print ("==============      FISCO-BCOS      start...  ==============")
    if_exist_fisco = getCommProperties("if.exist.fisco")
    fisco_dir = getCommProperties("fisco.dir")
    if if_exist_fisco == "no":
        fisco_dir = currentDir + "/nodes/127.0.0.1"
    
    if not os.path.exists(fisco_dir + "/start_all.sh"):
        print ("======= FISCO-BCOS dir:{} is not correct. please check! =======".format(fisco_dir))
        sys.exit(0)
    os.chdir(fisco_dir)
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    os.system("bash start_all.sh")
    print ("==============      FISCO-BCOS      end...    ==============")
    return
    
def stopNode():
    if_exist_fisco = getCommProperties("if.exist.fisco")
    fisco_dir = getCommProperties("fisco.dir")
    if if_exist_fisco == "no":
        fisco_dir = currentDir + "/nodes/127.0.0.1"
    
    if not os.path.exists(fisco_dir + "/stop_all.sh"):
        print ("======= FISCO-BCOS dir:{} is not correct. please check! =======".format(fisco_dir))
        sys.exit(0)
    os.chdir(fisco_dir)
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
    doCmd('sed -i "s/5000/{}/g" {}/comm/nginx.conf'.format(web_port, currentDir))
    doCmd('sed -i "s/server 127.0.0.1:5001/server {}:{}/g" {}/comm/nginx.conf'.format(deploy_ip, mgr_port, currentDir))
    doCmd('sed -i "s:log_path:{}:g" {}/comm/nginx.conf'.format(web_log_dir, currentDir))
    doCmd('sed -i "s:web_page_url:{}:g" {}/comm/nginx.conf'.format(web_dir, currentDir))

    return

def installWeb():
    print ("================================================================")
    print ("==============      WeBASE-Web     install... ==============")
    os.chdir(currentDir)
    version = getCommProperties("webase.version")
    gitComm = "wget https://www.fisco.com.cn/cdn/webase/releases/download/{}/webase-web.zip".format(version)
    pullSourceExtract(gitComm,"webase-web")
    changeWebConfig()
    startWeb()
    
def startWeb():
    print ("==============      WeBASE-Web      start...  ==============")
    if os.path.exists("/run/nginx-webase-web.pid"):
        info = "n"
        if sys.version_info.major == 2:
            info = raw_input("WeBASE-Web进程已经存在，是否kill进程强制重启？[y/n]:")
        else:
            info = input("WeBASE-Web进程已经存在，是否kill进程强制重启？[y/n]:")
        if info == "y" or info == "Y":
            fin = open('/run/nginx-webase-web.pid', 'r')
            pid = fin.read()
            cmd = "sudo kill -QUIT {}".format(pid)
            os.system(cmd)
            doCmdIgnoreException("sudo rm -rf /run/nginx-webase-web.pid")
        else:
            sys.exit(0)
    web_log_dir = currentDir + "/webase-web/log"
    doCmd('mkdir -p {}'.format(web_log_dir))
    nginx_config_dir = currentDir + "/comm/nginx.conf"
    res = doCmd("which nginx")
    if res["status"] == 0:
        res2 = doCmd("sudo " + res["output"] + " -c " + nginx_config_dir)
        if res2["status"] == 0:
            print ("=======      WeBASE-Web     start success!  =======")
        else:
            print ("=======      WeBASE-Web     start  fail. Please view log file (default path:./webase-web/log/).    =======")
            sys.exit(0)
    else:
        print ("=======      WeBASE-Web     start  fail. Please view log file (default path:./log/).    =======")
        sys.exit(0)
    print ("==============      WeBASE-Web      end...    ==============")
    return
    
def stopWeb():
    if os.path.exists("/run/nginx-webase-web.pid"):
        fin = open('/run/nginx-webase-web.pid', 'r')
        pid = fin.read()
        cmd = "sudo kill -QUIT {}".format(pid)
        os.system(cmd)
        doCmdIgnoreException("sudo rm -rf /run/nginx-webase-web.pid")
        print ("=======      WeBASE-Web     stop  success!  =======")
    else:
        print ("=======      WeBASE-Web     is not running! =======")
    return

def changeManagerConfig():
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
    doCmd('sed -i "s/webasenodemanager/{}/g" {}/webase.sh'.format(mysql_database, script_dir))
    
    # change server config
    doCmd('sed -i "s/5001/{}/g" {}/application.yml'.format(mgr_port, conf_dir))
    doCmd('sed -i "s/127.0.0.1/{}/g" {}/application.yml'.format(mysql_ip, conf_dir))
    doCmd('sed -i "s/3306/{}/g" {}/application.yml'.format(mysql_port, conf_dir))
    doCmd('sed -i "s/defaultAccount/{}/g" {}/application.yml'.format(mysql_user, conf_dir))
    doCmd('sed -i "s/defaultPassword/{}/g" {}/application.yml'.format(mysql_password, conf_dir))
    doCmd('sed -i "s/webasenodemanager/{}/g" {}/application.yml'.format(mysql_database, conf_dir))

    return
    
def installManager():
    print ("================================================================")
    print ("============== WeBASE-Node-Manager install... ==============")
    os.chdir(currentDir)
    version = getCommProperties("webase.version")
    gitComm = "wget https://www.fisco.com.cn/cdn/webase/releases/download/{}/webase-node-mgr.zip".format(version)
    pullSourceExtract(gitComm,"webase-node-mgr")
    changeManagerConfig()
    dbConnect()
    
    mysql_ip = getCommProperties("mysql.ip")
    mysql_port = getCommProperties("mysql.port")
    server_dir = currentDir + "/webase-node-mgr"
    script_dir = server_dir + "/script"
    
    if len(sys.argv) == 3 and sys.argv[2] == "travis":
        print ("Travis CI 不初始化数据库") 
    else:
        info = "n"
        if sys.version_info.major == 2:
            info = raw_input("是否初始化数据(首次部署或重建库需执行)？[y/n]:")
        else:
            info = input("是否初始化数据(首次部署或重建库需执行)？[y/n]:")
        if info == "y" or info == "Y":
            os.chdir(script_dir)
            doCmdIgnoreException("chmod u+x *.sh")
            doCmdIgnoreException("dos2unix *.sh")
            dbResult = doCmd('bash webase.sh {} {}'.format(mysql_ip, mysql_port))
            if dbResult["status"] == 0:
                if_success = 'success' in dbResult["output"]
                if if_success:
                    print ("======= script init success! =======")
                else:
                    print ("======= script init  fail!   =======")
                    print (dbResult["output"])
                    sys.exit(0)
            else:
                print ("======= script init  fail. Please view log file (default path:./log/).   =======")
                sys.exit(0)
    startManager()
    return
    
def startManager():
    print ("============== WeBASE-Node-Manager  start...  ==============")
    os.chdir(currentDir)
    managerPort = getCommProperties("front.port")
    server_dir = currentDir + "/webase-node-mgr"
    os.chdir(server_dir)
    doCmdIgnoreException("source /etc/profile")
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    result = doCmd("bash start.sh")
    if result["status"] == 0:
        if_occupied = 'been occupied' in result["output"]
        if if_occupied:
            pid = get_str_btw(result["output"], "(", ")")
            print ("Port {} has been occupied by other server PID({})".format(managerPort,pid))
            sys.exit(0)
        if_started = 'is running' in result["output"]
        if if_started:
            pid = get_str_btw(result["output"], "(", ")")
            print ("WeBASE-Node-Manager Port {} is running PID({})".format(managerPort,pid))
            sys.exit(0)
        if_success = 'Success' in result["output"]
        if if_success:
            print ("======= WeBASE-Node-Manager start success!  =======")
        else:
            print ("======= WeBASE-Node-Manager start  fail. Please view log file (default path:./webase-node-mgr/log/).    =======")
            sys.exit(0)
    else:
        print ("======= WeBASE-Node-Manager start  fail. Please view log file (default path:./log/).    =======")
        sys.exit(0)
    print ("============== WeBASE-Node-Manager  end...    ==============")
    return
        
def stopManager():
    server_dir = currentDir + "/webase-node-mgr"
    os.chdir(server_dir)
    doCmdIgnoreException("source /etc/profile")
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    result = doCmd("bash stop.sh")
    if result["status"] == 0:
        if_success = 'Success' in result["output"]
        if if_success:
            print ("======= WeBASE-Node-Manager stop  success!  =======")
        else:
            print ("======= WeBASE-Node-Manager is not running! =======")
    else:
        print ("======= WeBASE-Node-Manager stop   fail. Please view log file (default path:./log/).    =======")
    return
        
def changeFrontConfig():
    # get properties
    deploy_ip = "127.0.0.1"
    mgr_port = getCommProperties("mgr.port")
    frontPort = getCommProperties("front.port")
    nodeListenIp = getCommProperties("node.listenIp")
    nodeChannelPort = getCommProperties("node.channelPort")
    frontDb = getCommProperties("front.h2.name")
    
    if_exist_fisco = getCommProperties("if.exist.fisco")
    fisco_dir = getCommProperties("fisco.dir")
    if if_exist_fisco == "no":
        fisco_dir = currentDir + "/nodes/127.0.0.1"

    # init file
    server_dir = currentDir + "/webase-front/conf"
    if not os.path.exists(server_dir + "/temp.yml"):
        doCmd('cp -f {}/application.yml {}/temp.yml'.format(server_dir, server_dir))
    else:
        doCmd('cp -f {}/temp.yml {}/application.yml'.format(server_dir, server_dir))
        
    # change server config
    doCmd('sed -i "s/5002/{}/g" {}/application.yml'.format(frontPort, server_dir))
    doCmd('sed -i "s/ip: 127.0.0.1/ip: {}/g" {}/application.yml'.format(nodeListenIp, server_dir))
    doCmd('sed -i "s/20200/{}/g" {}/application.yml'.format(nodeChannelPort, server_dir))
    doCmd('sed -i "s/keyServer: 127.0.0.1:5001/keyServer: {}:{}/g" {}/application.yml'.format(deploy_ip, mgr_port, server_dir))
    doCmd('sed -i "s%./h2/webasefront%../h2/{}%g" {}/application.yml'.format(frontDb, server_dir))
    doCmd('sed -i "s%monitorDisk: /%monitorDisk: {}%g" {}/application.yml'.format(fisco_dir, server_dir))

    return
    
def installFront():
    print ("================================================================")
    print ("==============     WeBASE-Front    install... ==============")
    os.chdir(currentDir)
    version = getCommProperties("webase.version")
    gitComm = "wget https://www.fisco.com.cn/cdn/webase/releases/download/{}/webase-front.zip".format(version)
    pullSourceExtract(gitComm,"webase-front")
    changeFrontConfig()
    
    # check front db
    frontDb = getCommProperties("front.h2.name")
    db_dir = currentDir+"/h2"
    doCmdIgnoreException("mkdir -p {}".format(db_dir))
    res_file = checkFileName(db_dir,frontDb)
    if res_file:
        info = "n"
        if sys.version_info.major == 2:
            info = raw_input("WeBASE-Front数据库{}已经存在，是否删除重建？[y/n]:".format(frontDb))
        else:
            info = input("WeBASE-Front数据库{}已经存在，是否删除重建？[y/n]:".format(frontDb))
        if info == "y" or info == "Y":
            doCmdIgnoreException("rm -rf {}/{}.*".format(db_dir,frontDb))
    
    # copy node crt
    if_exist_fisco = getCommProperties("if.exist.fisco")
    fisco_dir = getCommProperties("fisco.dir")
    if if_exist_fisco == "no":
        fisco_dir = currentDir + "/nodes/127.0.0.1"
    sdk_dir = fisco_dir + "/sdk"
    if not os.path.exists(sdk_dir):
        print ("======= FISCO-BCOS sdk dir:{} is not exist. please check! =======".format(sdk_dir))
        sys.exit(0)
    server_dir = currentDir + "/webase-front"
    os.chdir(server_dir)
    copyFiles(fisco_dir + "/sdk", server_dir + "/conf")
    
    startFront()
    return
    
def startFront():
    print ("==============     WeBASE-Front     start...  ==============")
    os.chdir(currentDir)
    frontPort = getCommProperties("front.port")
    server_dir = currentDir + "/webase-front"
    os.chdir(server_dir)
    doCmdIgnoreException("source /etc/profile")
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    result = doCmd("bash start.sh")
    if result["status"] == 0:
        if_occupied = 'been occupied' in result["output"]
        if if_occupied:
            pid = get_str_btw(result["output"], "(", ")")
            print ("Port {} has been occupied by other server PID({})".format(frontPort,pid))
            sys.exit(0)
        if_started = 'is running' in result["output"]
        if if_started:
            pid = get_str_btw(result["output"], "(", ")")
            print ("WeBASE-Front Port {} is running PID({})".format(frontPort,pid))
            sys.exit(0)
        if_success = 'Success' in result["output"]
        if if_success:
            print ("=======     WeBASE-Front    start success!  =======")
        else:
            print ("=======     WeBASE-Front    start  fail. Please view log file (default path:./webase-front/log/).    =======")
            sys.exit(0)
    else:
        print ("=======     WeBASE-Front    start  fail. Please view log file (default path:./log/).    =======")
        sys.exit(0)
    print ("==============     WeBASE-Front     end...    ==============")
    print ("================================================================")
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
            print ("=======     WeBASE-Front    stop  success!  =======")
        else:
            print ("=======     WeBASE-Front    is not running! =======")
    else:
        print ("=======     WeBASE-Front    stop   fail. Please view log file (default path:./log/).    =======")
    return
