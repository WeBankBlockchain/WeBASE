#!/usr/bin/python3
# encoding: utf-8

import sys
import os
import time
from .utils import *
from .mysql import *
import comm.docker as docker

baseDir = getBaseDir()
currentDir = getCurrentBaseDir()
# check init node mgr's tb_front 
initDbEnable = False
serverWaitTime = 5

def do():
    print ("==============        starting  deploy        ==============")
    installNode()
    installSign()
    installFront()
    installManager()
    installWeb()
    initFrontForMgr()
    print ("============================================================")
    print ("==============      deploy  has completed     ==============")
    print ("============================================================")
    os.chdir(currentDir)
    web_version = getCommProperties("webase.web.version")
    mgr_version = getCommProperties("webase.mgr.version")
    sign_version = getCommProperties("webase.sign.version")
    front_version = getCommProperties("webase.front.version")

    print ("==============    webase-web version  {}        ========".format(web_version))
    print ("==============    webase-node-mgr version  {}   ========".format(mgr_version))
    print ("==============    webase-sign version  {}       ========".format(sign_version))
    print ("==============    webase-front version  {}      ========".format(front_version))
    print ("============================================================")
    return

def visual_do():
    print ("==============        starting  deploy        ==============")
    installDockerImage()
    installSign()
    installManager(True)
    installWeb()
    print ("============================================================")
    print ("==============      deploy  has completed     ==============")
    print ("============================================================")
    os.chdir(currentDir)
    web_version = getCommProperties("webase.web.version")
    mgr_version = getCommProperties("webase.mgr.version")
    sign_version = getCommProperties("webase.sign.version")

    print ("==============    webase-web version  {}        ========".format(web_version))
    print ("==============    webase-node-mgr version  {}   ========".format(mgr_version))
    print ("==============    webase-sign version  {}       ========".format(sign_version))
    print ("============================================================")
    return

# docker-compose do
def docker_do():
    print ("==============        starting  deploy        ==============")
    # build chain by -d (docker mode) and start by docker(start_all.sh)
    installNode(True)
    docker.installDockerAll()
    print ("============================================================")
    print ("==============      deploy  has completed     ==============")
    print ("============================================================")
    os.chdir(currentDir)
    web_version = getCommProperties("webase.web.version")
    mgr_version = getCommProperties("webase.mgr.version")
    sign_version = getCommProperties("webase.sign.version")
    front_version = getCommProperties("webase.front.version")

    print ("==============    webase-web version  {}        ========".format(web_version))
    print ("==============    webase-node-mgr version  {}   ========".format(mgr_version))
    print ("==============    webase-sign version  {}       ========".format(sign_version))
    print ("==============    webase-front version  {}      ========".format(front_version))
    print ("============================================================")
    print ("======= check logs by [docker-compose -f docker/docker-compose.yaml logs -f]")
    return

def start():
    startNode()
    startSign()
    startFront()
    startManager()
    startWeb()
    return

def end():
    stopWeb()
    stopManager()
    stopFront()
    stopSign()
    stopNode()
    return

def visualStart():
    startSign()
    startManager()
    startWeb()
    return
def visualEnd():
    stopWeb()
    stopManager()
    stopSign()
    return

def dockerStartAll():
    print ("start nodes...")
    startNode()
    print ("start WeBASE by docker-compose...")
    docker.startDockerCompose()
    print ("Successfully start WeBASE by docker-compose...(30 seconds or more)")
    print ("Please check by [docker ps]")

def dockerEndAll():
    print ("stop WeBASE by docker-compose...(30 seconds or more)")
    docker.stopDockerCompose()
    print ("stop nodes...")
    stopNode()

def dockerStart():
    print ("start WeBASE by docker-compose...(30 seconds or more)")
    docker.startDockerCompose()
    print ("Please check by [docker ps]")

def dockerEnd():
    print ("stop WeBASE by docker-compose...(30 seconds or more)")
    docker.stopDockerCompose()

def dockerPull():
    print ("start pull docker compose images...")
    docker.pullDockerComposeImages()

def installNode(docker_mode=False):
    if_exist_fisco = getCommProperties("if.exist.fisco")
    node_p2pPort = int(getCommProperties("node.p2pPort"))
    node_channelPort = int(getCommProperties("node.channelPort"))
    node_rpcPort = int(getCommProperties("node.rpcPort"))
    fisco_version = getCommProperties("fisco.version")
    node_counts = getCommProperties("node.counts")
    encrypt_type = int(getCommProperties("encrypt.type"))
    encrypt_ssl_type = int(getCommProperties("encrypt.sslType"))
    docker_on = 1 if docker_mode is True else 0


    if if_exist_fisco == "no":
        print ("============================================================")
        print ("==============      Installing FISCO-BCOS     ==============")
        # init configure file
        if not os.path.exists(currentDir + "/nodetemp"):
            doCmd('cp -f nodeconf nodetemp')
        else:
            doCmd('cp -f nodetemp nodeconf')

        node_nums = 2
        if node_counts != "nodeCounts":
            node_nums = int(node_counts)
        doCmd('sed -i "s/nodeCounts/{}/g" nodeconf'.format(node_nums))
        doCmdIgnoreException("dos2unix nodeconf")

        # gitComm = "wget https://github.com/FISCO-BCOS/FISCO-BCOS/releases/download/v{}/build_chain.sh && chmod u+x build_chain.sh".format(fisco_version)
        gitComm = "wget https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/FISCO-BCOS/FISCO-BCOS/releases/v{}/build_chain.sh && chmod u+x build_chain.sh".format(fisco_version)
        if os.path.exists("{}/build_chain.sh".format(currentDir)):
            info = "n"      
            if sys.version_info.major == 2:
                info =  raw_input("Build chain script “build_chain.sh” already exists. Re-download it or not? [y/n]: ")
            else:
                info = input("Build chain script “build_chain.sh” already exists. Re-download it or not? [y/n]: ")
            if info == "y" or info == "Y":
                doCmd("rm -f build_chain.sh")
                # download build_chain script
                print (gitComm)
                os.system(gitComm)
        else:
            # download build_chain script
            print (gitComm)
            os.system(gitComm)
        # if no nodes directory, run build_chain script
        if not os.path.exists("{}/nodes".format(currentDir)):
            # guomi 
            if encrypt_type == 1:
                # guomi ssl
                if encrypt_ssl_type == 1:
                    if docker_on == 1:
                        os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i -g -G -d".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
                    else: 
                        os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i -g -G".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
                # standard ssl
                else:
                    if docker_on == 1:
                        os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i -g -d".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
                    else:
                        os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i -g".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
            else:
                if docker_on == 1:
                    os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i -d".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
                else:
                    os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
        else:
            info = "n"
            if sys.version_info.major == 2:
                info = raw_input("FISCO-BCOS node directory “nodes” already exists. Reinstall or not?[y/n]:")
            else:
                info = input("FISCO-BCOS node directory “nodes” already exists. Reinstall or not?[y/n]:")
            if info == "y" or info == "Y":
                doCmdIgnoreException("bash nodes/127.0.0.1/stop_all.sh")
                doCmd("rm -rf nodes")
                # guomi 
                if encrypt_type == 1:
                    # guomi ssl
                    if encrypt_ssl_type == 1:
                        if docker_on == 1:
                            os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i -g -G -d".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))                        
                        else:
                            os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i -g -G".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
                    # standard ssl
                    else:
                        if docker_on == 1:
                            os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i -g -d".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))                            
                        else:
                            os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i -g".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
                else:
                    if docker_on == 1:
                        os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i -d".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))                    
                    else:
                        os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
    startNode()

def startNode():
    print ("==============      Starting FISCO-BCOS       ==============")
    if_exist_fisco = getCommProperties("if.exist.fisco")
    if if_exist_fisco is None:
        print ("======= FISCO-BCOS is not deploy. return! =======")
        return

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
    print ("==============      FISCO-BCOS  Started       ==============")
    return

def stopNode():
    os.chdir(currentDir)
    if_exist_fisco = getCommProperties("if.exist.fisco")
    if if_exist_fisco is None:
        print ("=======   FISCO-BCOS is not deploy. return! =======")
        return

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
    pid_file = currentDir + "/nginx-webase-web.pid"

    # init configure file
    web_conf_dir = currentDir + "/comm"
    if not os.path.exists(web_conf_dir + "/temp.conf"):
        doCmd('cp -f {}/nginx.conf {}/temp.conf'.format(web_conf_dir, web_conf_dir))
    else:
        doCmd('cp -f {}/temp.conf {}/nginx.conf'.format(web_conf_dir, web_conf_dir))

    # change web config
    web_dir = currentDir + "/webase-web"
    h5_enable = int(getCommProperties("web.h5.enable"))
    h5_web_dir = web_dir
    if h5_enable == 1:
        # mobile phone h5 dir
        h5_web_dir = currentDir + "/webase-web-mobile"
    web_log_dir = web_dir + "/log"
    doCmd('mkdir -p {}'.format(web_log_dir))
    doCmd('sed -i "s/127.0.0.1/{}/g" {}/comm/nginx.conf'.format(deploy_ip, currentDir))
    doCmd('sed -i "s/5000/{}/g" {}/comm/nginx.conf'.format(web_port, currentDir))
    doCmd('sed -i "s/server 127.0.0.1:5001/server {}:{}/g" {}/comm/nginx.conf'.format(deploy_ip, mgr_port, currentDir))
    doCmd('sed -i "s:log_path:{}:g" {}/comm/nginx.conf'.format(web_log_dir, currentDir))
    doCmd('sed -i "s:pid_file:{}:g" {}/comm/nginx.conf'.format(pid_file, currentDir))
    # set web_page_url(root & static) globally
    doCmd('sed -i "s:web_page_url:{}:g" {}/comm/nginx.conf'.format(web_dir, currentDir))
    # set mobile phone phone_page_url globally
    doCmd('sed -i "s:phone_page_url:{}:g" {}/comm/nginx.conf'.format(h5_web_dir, currentDir))

    # change the path of mime.types, which is in the path of nginx configuration by default.
    res = doCmd("which nginx")
    if res["status"] == 0:
        res2 = doCmd("sudo " + res["output"] + " -t ")
        if res2["status"] == 0:
           oneLineOutput = res2["output"].split('\n')[0]; 
           print("onelineOutput: %s" %(oneLineOutput));
           startIndex = oneLineOutput.index("/");
           endIndex = oneLineOutput.rindex("/");

           nginxConfPath = oneLineOutput[startIndex:endIndex];
           print("Defualt nginx config path: %s" %(nginxConfPath)); 
           doCmd('sed -i "s/include .*\/mime.types/include {}\/mime.types/g" {}/comm/nginx.conf'.format(nginxConfPath.replace("/", "\/"), currentDir))
        else:
            print ("==============   WebBASE-web start fail when checking the path of nginx configuration fail. Please view log file (default path:./webase-web/log/). ==============")
            sys.exit(0)
    else:
        print ("==============    WeBASE-Web start fail when getting nginx. Please view log file (default path:./webase-web/log/). ==============")
        sys.exit(0)

    return

def installWeb():
    print ("============================================================")
    print ("==============      Installing WeBASE-Web     ==============")
    os.chdir(currentDir)
    web_version = getCommProperties("webase.web.version")
    gitComm = "wget https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/{}/webase-web.zip ".format(web_version)
    pullSourceExtract(gitComm,"webase-web")
    web_h5_enable = int(getCommProperties("web.h5.enable"))
    if web_h5_enable == 1:
        gitComm = "wget https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/{}/webase-web-mobile.zip ".format(web_version)
        pullSourceExtract(gitComm,"webase-web-mobile")    
    changeWebConfig()
    startWeb()

def startWeb():
    print ("==============      Starting WeBASE-Web       ==============")
    pid_file = currentDir + "/nginx-webase-web.pid"
    if os.path.exists(pid_file):
        info = "n"
        if sys.version_info.major == 2:
            info = raw_input("WeBASE-Web Process already exists. Kill process to force restart?[y/n]:")
        else:
            info = input("WeBASE-Web Process already exists. Kill process to force restart?[y/n]:")
        if info == "y" or info == "Y":
            fin = open(pid_file, 'r')
            pid = fin.read()
            cmd = "sudo kill -QUIT {}".format(pid)
            os.system(cmd)
            doCmdIgnoreException("sudo rm -rf " + pid_file)
        else:
            sys.exit(0)
    web_log_dir = currentDir + "/webase-web/log"
    doCmd('mkdir -p {}'.format(web_log_dir))
    nginx_config_dir = currentDir + "/comm/nginx.conf"
    res = doCmd("which nginx")
    if res["status"] == 0:
        res2 = doCmd("sudo " + res["output"] + " -c " + nginx_config_dir)
        if res2["status"] != 0:
            print ("==============    WeBASE-Web start fail. Please view log file (default path:./webase-web/log/). ==============")
            sys.exit(0)
    else:
        print ("==============    WeBASE-Web start fail. Please view log file (default path:./webase-web/log/). ==============")
        sys.exit(0)
    print ("==============      WeBASE-Web Started        ==============")
    return

def stopWeb():
    pid_file = currentDir + "/nginx-webase-web.pid"
    if os.path.exists(pid_file):
        fin = open(pid_file, 'r')
        pid = fin.read()
        cmd = "sudo kill -QUIT {}".format(pid)
        os.system(cmd)
        doCmdIgnoreException("sudo rm -rf " + pid_file)
        print ("=======      WeBASE-Web     stop  success!  =======")
    else:
        print ("=======      WeBASE-Web     is not running! =======")
    return

def changeManagerConfig(visual_deploy=False):
    # get properties
    sign_port = getCommProperties("sign.port")
    mgr_port = getCommProperties("mgr.port")
    mysql_ip = getCommProperties("mysql.ip")
    mysql_port = getCommProperties("mysql.port")
    mysql_user = getCommProperties("mysql.user")
    mysql_password = getCommProperties("mysql.password")
    mysql_database = getCommProperties("mysql.database")
    encrypt_type = int(getCommProperties("encrypt.type"))
    deploy_type = 1 if visual_deploy is True else 0

    if visual_deploy:
        sign_ip = getCommProperties("sign.ip")

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
    doCmd('sed -i "s%encryptType: 0%encryptType: {}%g" {}/application.yml'.format(encrypt_type, conf_dir))
    doCmd('sed -i "s%deployType:.*$%deployType: {}%g" {}/application.yml'.format(deploy_type, conf_dir))

    if visual_deploy:
        if (sign_ip == '127.0.0.1' or sign_ip == 'localhost'):
            print ("ERROR! If using visual deploy, webaseSignAddress cannot be 127.0.0.1 or localhost!")
        doCmd('sed -i "s%webaseSignAddress:.*$%webaseSignAddress: {}:{}%g" {}/application.yml'.format(sign_ip, sign_port, conf_dir))

    return

def installManager(visual_deploy=False):
    print ("============================================================")
    print ("============== Installing WeBASE-Node-Manager ==============")
    os.chdir(currentDir)
    mgr_version = getCommProperties("webase.mgr.version")
    encrypt_type = int(getCommProperties("encrypt.type"))
    gitComm = "wget https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/{}/webase-node-mgr.zip ".format(mgr_version)
    pullSourceExtract(gitComm,"webase-node-mgr")
    changeManagerConfig(visual_deploy)
    
    # v1.4.2 use py to init, instead of .sh to call mysql client
    # connect mgr's db and create database
    # if no re-create db, no need to init tables in db
    whether_init = mgrDbInit()
    server_dir = currentDir + "/webase-node-mgr"
    script_dir = server_dir + "/script"    
    if len(sys.argv) == 3 and sys.argv[2] == "travis":
        print ("Travis CI do not initialize database")
    elif whether_init == True:
        initNodeMgrTable(script_dir)
        global initDbEnable
        initDbEnable = True
        log.info(" installManager initDbEnable {}".format(initDbEnable))
        
    startManager()
    return        

def startManager():
    print ("==============  Starting WeBASE-Node-Manager  ==============")
    os.chdir(currentDir)
    managerPort = getCommProperties("mgr.port")
    server_dir = currentDir + "/webase-node-mgr"
    if not checkPathExists(server_dir):
        sys.exit(0)
    os.chdir(server_dir)
    
    doCmdIgnoreException("source /etc/profile")
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    result = doCmd("bash start.sh")
    if result["status"] == 0:
        if_started = 'is running' in result["output"]
        if if_started:
            pid = get_str_btw(result["output"], "(", ")")
            print ("WeBASE-Node-Manager Port {} is running PID({})".format(managerPort,pid))
            sys.exit(0)
        if_success = 'Starting' in result["output"]
        if if_success:
            timeTemp = 0
            while timeTemp < serverWaitTime :
                print("=", end='')
                sys.stdout.flush()
                time.sleep(1)
                timeTemp = timeTemp + 1
            print ("========= WeBASE-Node-Manager starting. Please check through the log file (default path:./webase-node-mgr/log/). ==============")
        else:
            print ("============== WeBASE-Node-Manager start fail. Please check through the log file (default path:./webase-node-mgr/log/). ==============")
            sys.exit(0)
    else:
        print ("============== WeBASE-Node-Manager start fail. Please check through the log file (default path:./webase-node-mgr/log/). ==============")
        sys.exit(0)
    print ("==============  WeBASE-Node-Manager  Started  ==============")
    return

def stopManager():
    server_dir = currentDir + "/webase-node-mgr"
    if not checkPathExists(server_dir):
        return
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
    sign_port = getCommProperties("sign.port")
    frontPort = getCommProperties("front.port")
    nodeListenIp = getCommProperties("node.listenIp")
    nodeChannelPort = getCommProperties("node.channelPort")
    frontDb = getCommProperties("front.h2.name")
    #encrypt_type = int(getCommProperties("encrypt.type"))

    if_exist_fisco = getCommProperties("if.exist.fisco")
    fisco_dir = getCommProperties("fisco.dir")
    node_dir = getCommProperties("node.dir")
    final_node_dir = fisco_dir + "/" + node_dir
    if if_exist_fisco == "no":
        fisco_dir = currentDir + "/nodes/127.0.0.1"
        final_node_dir = currentDir + "/nodes/127.0.0.1/node0"

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
    #doCmd('sed -i "s%encryptType: 0%encryptType: {}%g" {}/application.yml'.format(encrypt_type, server_dir))
    doCmd('sed -i "s/keyServer: 127.0.0.1:5004/keyServer: {}:{}/g" {}/application.yml'.format(deploy_ip, sign_port, server_dir))
    doCmd('sed -i "s%/webasefront%/{}%g" {}/application.yml'.format(frontDb, server_dir))
    doCmd('sed -i "s%monitorDisk: /%monitorDisk: {}%g" {}/application.yml'.format(fisco_dir, server_dir))
    doCmd('sed -i "s%nodePath: /fisco/nodes/127.0.0.1/node0%nodePath: {}%g" {}/application.yml'.format(final_node_dir, server_dir))

    return

def installFront():
    print ("============================================================")
    print ("==============     Installing WeBASE-Front    ==============")
    os.chdir(currentDir)
    front_version = getCommProperties("webase.front.version")
    gitComm = "wget https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/{}/webase-front.zip ".format(front_version)
    frontPackage = "webase-front"
    server_dir = currentDir + "/" + frontPackage
    pullSourceExtract(gitComm,frontPackage)
    changeFrontConfig()

    # check front db
    frontDb = getCommProperties("front.h2.name")
    db_dir = currentDir+"/h2"
    doCmdIgnoreException("mkdir -p {}".format(db_dir))
    res_file = checkFileName(db_dir,frontDb)
    if res_file:
        info = "n"
        if sys.version_info.major == 2:
            info = raw_input("WeBASE-Front database {} already exists, rebuild or not?[y/n]:".format(frontDb))
        else:
            info = input("WeBASE-Front database {} already exists, rebuild or not?[y/n]:".format(frontDb))
        if info == "y" or info == "Y":
            doCmdIgnoreException("rm -rf {}/{}.*".format(db_dir,frontDb))

    # copy node crt
    if_exist_fisco = getCommProperties("if.exist.fisco")
    fisco_dir = getCommProperties("fisco.dir")
    #encrypt_ssl_type = int(getCommProperties("encrypt.sslType"))

    if if_exist_fisco == "no":
        fisco_dir = currentDir + "/nodes/127.0.0.1"
    sdk_dir = fisco_dir + "/sdk"
    if not os.path.exists(sdk_dir):
        print ("======= FISCO-BCOS sdk dir:{} is not exist. please check! =======".format(sdk_dir))
        sys.exit(0)
    os.chdir(server_dir)
    # copy the whole sdk(sdk.key and gm dir) to conf/
    copyFiles(fisco_dir + "/sdk", server_dir + "/conf")

    startFront()
    return

def startFront():
    print ("==============     Starting WeBASE-Front      ==============")
    os.chdir(currentDir)
    frontPort = getCommProperties("front.port")
    if frontPort is None:
        print ("======= WeBASE-Front is not deploy. return! =======")
        return

    server_dir = currentDir + "/webase-front"
    if not checkPathExists(server_dir):
        sys.exit(0)
    os.chdir(server_dir)
    
    doCmdIgnoreException("source /etc/profile")
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    result = doCmd("bash start.sh")
    if result["status"] == 0:
        if_started = 'is running' in result["output"]
        if if_started:
            pid = get_str_btw(result["output"], "(", ")")
            print ("WeBASE-Front Port {} is running PID({})".format(frontPort,pid))
            sys.exit(0)
        if_success = 'Starting' in result["output"]
        if if_success:
            timeTemp = 0
            while timeTemp < serverWaitTime :
                print("=", end='')
                sys.stdout.flush()
                time.sleep(1)
                timeTemp = timeTemp + 1
            print ("========= WeBASE-Front starting. Please check through the log file (default path:./webase-front/log/). ==============")
        else:
            print ("============== WeBASE-Front start fail. Please check through the log file (default path:./webase-front/log/). ==============")
            sys.exit(0)
    else:
        print ("============== WeBASE-Front start fail. Please check through the log file (default path:./{}/log/). ==============")
        sys.exit(0)
    print ("==============     WeBASE-Front  Started.     ==============")
    return

def stopFront():
    os.chdir(currentDir)
    server_dir = currentDir + "/webase-front"
    if not checkPathExists(server_dir):
        return
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

def changeSignConfig():
    # get properties
    sign_port = getCommProperties("sign.port")
    mysql_ip = getCommProperties("sign.mysql.ip")
    mysql_port = getCommProperties("sign.mysql.port")
    mysql_user = getCommProperties("sign.mysql.user")
    mysql_password = getCommProperties("sign.mysql.password")
    mysql_database = getCommProperties("sign.mysql.database")

    # init file
    server_dir = currentDir + "/webase-sign"
    conf_dir = server_dir + "/conf"
    if not os.path.exists(conf_dir + "/temp.yml"):
        doCmd('cp -f {}/application.yml {}/temp.yml'.format(conf_dir, conf_dir))
    else:
        doCmd('cp -f {}/temp.yml {}/application.yml'.format(conf_dir, conf_dir))

    # change server config
    doCmd('sed -i "s/5004/{}/g" {}/application.yml'.format(sign_port, conf_dir))
    doCmd('sed -i "s/127.0.0.1/{}/g" {}/application.yml'.format(mysql_ip, conf_dir))
    doCmd('sed -i "s/3306/{}/g" {}/application.yml'.format(mysql_port, conf_dir))
    doCmd('sed -i "s/dbUsername/{}/g" {}/application.yml'.format(mysql_user, conf_dir))
    doCmd('sed -i "s/dbPassword/{}/g" {}/application.yml'.format(mysql_password, conf_dir))
    doCmd('sed -i "s/webasesign/{}/g" {}/application.yml'.format(mysql_database, conf_dir))

    return

def installSign():
    print ("============================================================")
    print ("==============     Installing WeBASE-Sign     ==============")
    os.chdir(currentDir)
    sign_version = getCommProperties("webase.sign.version")
    gitComm = "wget https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/{}/webase-sign.zip".format(sign_version)
    pullSourceExtract(gitComm,"webase-sign")
    changeSignConfig()
    signDbInit()
    startSign()
    return

# download by visual deploy
# deprecated in 1.4.3
def installDockerImage():
    ifLoad = getCommProperties("if.load.image")
    if (ifLoad == "yes"):
        print ("============================================================")
        print ("============ Download docker image from CDN... =============")
        os.chdir(currentDir)
        image_version = getCommProperties("fisco.webase.docker.cdn.version")
        gitComm = "wget https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/{}/docker-fisco-webase.tar".format(image_version)
        pullDockerImage(gitComm,"docker-fisco-webase.tar","fiscoorg/fisco-webase")
    else: 
        print ("============ Skip download docker image from CDN... =============")
    return

def startSign():
    print ("==============      Starting WeBASE-Sign      ==============")
    os.chdir(currentDir)
    signPort = getCommProperties("sign.port")
    server_dir = currentDir + "/webase-sign"
    if not checkPathExists(server_dir):
        sys.exit(0)
    os.chdir(server_dir)
    
    doCmdIgnoreException("source /etc/profile")
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    result = doCmd("bash start.sh")
    if result["status"] == 0:
        if_started = 'is running' in result["output"]
        if if_started:
            pid = get_str_btw(result["output"], "(", ")")
            print ("WeBASE-Sign Port {} is running PID({})".format(signPort,pid))
            sys.exit(0)
        if_success = 'Starting' in result["output"]
        if if_success:
            timeTemp = 0
            while timeTemp < serverWaitTime :
                print("=", end='')
                sys.stdout.flush()
                time.sleep(1)
                timeTemp = timeTemp + 1
            print ("========= WeBASE-Sign starting. Please check through the log file (default path:./webase-sign/log/). ==============")
        else:
            print ("============== WeBASE-Sign start fail. Please check through the log file (default path:./webase-sign/log/). ==============")
            sys.exit(0)
    else:
        print ("============== WeBASE-Sign start fail. Please check through the log file (default path:./webase-sign/log/). ==============")
        sys.exit(0)
    print ("==============      WeBASE-Sign  Started      ==============")
    return

def stopSign():
    server_dir = currentDir + "/webase-sign"
    if not checkPathExists(server_dir):
        return
    os.chdir(server_dir)
    doCmdIgnoreException("source /etc/profile")
    doCmdIgnoreException("chmod u+x *.sh")
    doCmdIgnoreException("dos2unix *.sh")
    result = doCmd("bash stop.sh")
    if result["status"] == 0:
        if_success = 'Success' in result["output"]
        if if_success:
            print ("=======     WeBASE-Sign     stop  success!  =======")
        else:
            print ("=======     WeBASE-Sign     is not running! =======")
    else:
        print ("======= WeBASE-Sign stop fail. Please view log file (default path:./log/).    =======")
    return

def initFrontForMgr():
    os.chdir(currentDir)
    global initDbEnable
    log.info(" initFrontForMgr initDbEnable: {}".format(initDbEnable))
    if initDbEnable:
        print ("==============  Init Front for Mgr start...   ==============")
        managerPort = getCommProperties("mgr.port")
        frontPort = getCommProperties("front.port")
        url = "http://127.0.0.1:{}/WeBASE-Node-Manager/front/refresh".format(managerPort)
        timeTemp = 0
        waitTime = 120
        frontEnable = False
        while timeTemp < waitTime :
            print("=", end='')
            sys.stdout.flush()
            time.sleep(1)
            timeTemp = timeTemp + 1
            frontEnable = do_telnet("127.0.0.1",frontPort)
            nodemgrEnable = do_telnet("127.0.0.1",managerPort)
            if frontEnable and nodemgrEnable:
                log.info(" initFrontForMgr frontEnable {}".format(frontEnable))
                addFrontToDb()
                restResult = rest_get(url)
                if restResult == '':
                    print ("============== Init Front for Mgr fail. Please view log file (default path:./log/). ==============")
                else:
                    print("= 100%")
                    print ("==============  Init Front for Mgr end...     ==============")
                return
        if not frontEnable:
            print ("==============  Init Front for Mgr fail.      ==============")
            return
