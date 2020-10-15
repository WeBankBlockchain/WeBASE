#!/usr/bin/python3
# encoding: utf-8

import sys
import os
import time
from .utils import *
from .mysql import *

baseDir = getBaseDir()
currentDir = getCurrentBaseDir()
initDbEnable = False

def do():
    print ("=====================    deploy   start... =====================")
    installNode()
    installWeb()
    installManager()
    installSign()
    installFront()
    initFrontForMgr()
    print ("=====================    deploy   end...   =====================")
    os.chdir(currentDir)
    web_version = getCommProperties("webase.web.version")
    mgr_version = getCommProperties("webase.mgr.version")
    sign_version = getCommProperties("webase.sign.version")
    front_version = getCommProperties("webase.front.version")

    print ("=====================    webase-web version  {}        ==================".format(web_version))
    print ("=====================    webase-node-mgr version  {}   ==================".format(mgr_version))
    print ("=====================    webase-sign version  {}       ==================".format(sign_version))
    print ("=====================    webase-front version  {}      ==================".format(front_version))
    print ("================================================================")
    return

def visual_do():
    print ("=====================    deploy   start... =====================")
    installWeb()
    installManager(True)
    installSign()
    installDockerImage()
    print ("=====================    deploy   end...   =====================")
    os.chdir(currentDir)
    web_version = getCommProperties("webase.web.version")
    mgr_version = getCommProperties("webase.mgr.version")
    sign_version = getCommProperties("webase.sign.version")

    print ("=====================    webase-web version  {}        ==================".format(web_version))
    print ("=====================    webase-node-mgr version  {}   ==================".format(mgr_version))
    print ("=====================    webase-sign version  {}       ==================".format(sign_version))
    print ("================================================================")
    return


def start():
    startNode()
    startWeb()
    startManager()
    startSign()
    startFront()
    return

def end():
    stopNode()
    stopWeb()
    stopManager()
    stopSign()
    stopFront()
    return

def visualStart():
    startWeb()
    startManager()
    startSign()
    return
def visualEnd():
    stopWeb()
    stopManager()
    stopSign()
    return

def installNode():
    if_exist_fisco = getCommProperties("if.exist.fisco")
    node_p2pPort = int(getCommProperties("node.p2pPort"))
    node_channelPort = int(getCommProperties("node.channelPort"))
    node_rpcPort = int(getCommProperties("node.rpcPort"))
    fisco_version = getCommProperties("fisco.version")
    node_counts = getCommProperties("node.counts")
    encrypt_type = int(getCommProperties("encrypt.type"))

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
        doCmdIgnoreException("dos2unix nodeconf")

        gitComm = "wget https://github.com/FISCO-BCOS/FISCO-BCOS/releases/download/v{}/build_chain.sh && chmod u+x build_chain.sh".format(fisco_version)
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
            if encrypt_type == 1:
                os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i -g".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
            else:
                os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
        else:
            info = "n"
            if sys.version_info.major == 2:
                info = raw_input("FISCO-BCOS node directory “nodes” already exists. Reinstall or not？[y/n]:")
            else:
                info = input("FISCO-BCOS node directory “nodes” already exists. Reinstall or not？[y/n]:")
            if info == "y" or info == "Y":
                doCmdIgnoreException("bash nodes/127.0.0.1/stop_all.sh")
                doCmd("rm -rf nodes")
                if encrypt_type == 1:
                    os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i -g".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
                else:
                    os.system("bash build_chain.sh -f nodeconf -p {},{},{} -v {} -i".format(node_p2pPort, node_channelPort, node_rpcPort, fisco_version))
    startNode()

def startNode():
    print ("==============      FISCO-BCOS      start...  ==============")
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
    print ("==============      FISCO-BCOS      end...    ==============")
    return

def stopNode():
    if_exist_fisco = getCommProperties("if.exist.fisco")
    if if_exist_fisco is None:
        print ("======= FISCO-BCOS is not deploy. return! =======")
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
    web_version = getCommProperties("webase.web.version")
    gitComm = "wget https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/{}/webase-web.zip ".format(web_version)
    pullSourceExtract(gitComm,"webase-web")
    changeWebConfig()
    startWeb()

def startWeb():
    print ("==============      WeBASE-Web      start...  ==============")
    if os.path.exists("/run/nginx-webase-web.pid"):
        info = "n"
        if sys.version_info.major == 2:
            info = raw_input("WeBASE-Web Process already exists. Kill process to force restart？[y/n]:")
        else:
            info = input("WeBASE-Web Process already exists. Kill process to force restart？[y/n]:")
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
        ssh_user = getCommProperties("mgr.ssh.user")
        ssh_port = int(getCommProperties("mgr.ssh.port"))
        root_dir_on_host = getCommProperties("mgr.ssh.rootDirOnHost")

    # init file
    server_dir = currentDir + "/webase-node-mgr"
    script_dir = server_dir + "/script"
    script_dir_gm = script_dir + "/gm"
    conf_dir = server_dir + "/conf"
    if encrypt_type == 1:
        if not os.path.exists(script_dir_gm + "/temp-gm.sh"):
            doCmd('cp -f {}/webase-gm.sh {}/temp-gm.sh'.format(script_dir_gm, script_dir_gm))
        else:
            doCmd('cp -f {}/temp-gm.sh {}/webase-gm.sh'.format(script_dir_gm, script_dir_gm))
    else:
        if not os.path.exists(script_dir + "/temp.sh"):
            doCmd('cp -f {}/webase.sh {}/temp.sh'.format(script_dir, script_dir))
        else:
            doCmd('cp -f {}/temp.sh {}/webase.sh'.format(script_dir, script_dir))
    if not os.path.exists(conf_dir + "/temp.yml"):
        doCmd('cp -f {}/application.yml {}/temp.yml'.format(conf_dir, conf_dir))
    else:
        doCmd('cp -f {}/temp.yml {}/application.yml'.format(conf_dir, conf_dir))

    # change script config
    if encrypt_type == 1:
        doCmd('sed -i "s/defaultAccount/{}/g" {}/webase-gm.sh'.format(mysql_user, script_dir_gm))
        doCmd('sed -i "s/defaultPassword/{}/g" {}/webase-gm.sh'.format(mysql_password, script_dir_gm))
        doCmd('sed -i "s/webasenodemanager/{}/g" {}/webase-gm.sh'.format(mysql_database, script_dir_gm))
    else:
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
        doCmd('sed -i "s%webaseSignAddress:.*$%webaseSignAddress: {}:{}%g" {}/application.yml'.format(sign_ip, sign_port, conf_dir))
        doCmd('sed -i "s%sshDefaultUser:.*$%sshDefaultUser: {}%g" {}/application.yml'.format(ssh_user, conf_dir))
        doCmd('sed -i "s%sshDefaultPort:.*$%sshDefaultPort: {}%g" {}/application.yml'.format(ssh_port, conf_dir))
        doCmd('sed -i "s%rootDirOnHost:.*$%rootDirOnHost: {}%g" {}/application.yml'.format(root_dir_on_host,  conf_dir))

    return

def installManager(visual_deploy=False):
    print ("================================================================")
    print ("============== WeBASE-Node-Manager install... ==============")
    os.chdir(currentDir)
    mgr_version = getCommProperties("webase.mgr.version")
    encrypt_type = int(getCommProperties("encrypt.type"))
    gitComm = "wget https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/{}/webase-node-mgr.zip ".format(mgr_version)
    pullSourceExtract(gitComm,"webase-node-mgr")
    changeManagerConfig(visual_deploy)
    dbConnect()

    mysql_ip = getCommProperties("mysql.ip")
    mysql_port = getCommProperties("mysql.port")
    server_dir = currentDir + "/webase-node-mgr"
    script_dir = server_dir + "/script"
    script_cmd = 'bash webase.sh {} {}'.format(mysql_ip, mysql_port)
    if encrypt_type == 1:
        script_dir = script_dir + "/gm"
        script_cmd = 'bash webase-gm.sh {} {}'.format(mysql_ip, mysql_port)

    if len(sys.argv) == 3 and sys.argv[2] == "travis":
        print ("Travis CI do not initialize database")
    else:
        info = "n"
        if sys.version_info.major == 2:
            info = raw_input("Whether to initialize the data (the first deployment or rebuilding of the library needs to be performed)？[y/n]:")
        else:
            info = input("Whether to initialize the data (the first deployment or rebuilding of the library needs to be performed)？[y/n]:")
        if info == "y" or info == "Y":
            os.chdir(script_dir)
            doCmdIgnoreException("chmod u+x *.sh")
            doCmdIgnoreException("dos2unix *.sh")
            dbResult = doCmd(script_cmd)
            if dbResult["status"] == 0:
                if_success = 'success' in dbResult["output"]
                if if_success:
                    print ("======= script init success! =======")
                    global initDbEnable
                    initDbEnable = True
                    log.info(" installManager initDbEnable {}".format(initDbEnable))
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
    managerPort = getCommProperties("mgr.port")
    server_dir = currentDir + "/webase-node-mgr"
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
            print ("======= WeBASE-Node-Manager  starting . Please check through the log file (default path:./webase-node-mgr/log/). =======")
        else:
            print ("======= WeBASE-Node-Manager start fail. Please check through the log file (default path:./webase-node-mgr/log/). =======")
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
    sign_port = getCommProperties("sign.port")
    frontPort = getCommProperties("front.port")
    nodeListenIp = getCommProperties("node.listenIp")
    nodeChannelPort = getCommProperties("node.channelPort")
    frontDb = getCommProperties("front.h2.name")
    encrypt_type = int(getCommProperties("encrypt.type"))

    if_exist_fisco = getCommProperties("if.exist.fisco")
    fisco_dir = getCommProperties("fisco.dir")
    node_dir = getCommProperties("node.dir")
    if if_exist_fisco == "no":
        fisco_dir = currentDir + "/nodes/127.0.0.1"
        node_dir = currentDir + "/nodes/127.0.0.1/node0"

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
    doCmd('sed -i "s%encryptType: 0%encryptType: {}%g" {}/application.yml'.format(encrypt_type, server_dir))
    doCmd('sed -i "s/keyServer: 127.0.0.1:5004/keyServer: {}:{}/g" {}/application.yml'.format(deploy_ip, sign_port, server_dir))
    doCmd('sed -i "s%/webasefront%/{}%g" {}/application.yml'.format(frontDb, server_dir))
    doCmd('sed -i "s%monitorDisk: /%monitorDisk: {}%g" {}/application.yml'.format(fisco_dir, server_dir))
    doCmd('sed -i "s%nodePath: /fisco/nodes/127.0.0.1/node0%nodePath: {}%g" {}/application.yml'.format(node_dir, server_dir))

    return

def installFront():
    print ("================================================================")
    print ("==============     WeBASE-Front    install... ==============")
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
            info = raw_input("WeBASE-Front database {} already exists, delete rebuild or not？[y/n]:".format(frontDb))
        else:
            info = input("WeBASE-Front database {} already exists, delete rebuild or not？[y/n]:".format(frontDb))
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
    os.chdir(server_dir)
    copyFiles(fisco_dir + "/sdk", server_dir + "/conf")

    startFront()
    return

def startFront():
    print ("==============     WeBASE-Front     start...  ==============")
    os.chdir(currentDir)
    frontPort = getCommProperties("front.port")
    if frontPort is None:
        print ("======= WeBASE-Front is not deploy. return! =======")
        return

    frontPackage = "webase-front"
    os.chdir(currentDir + "/" + frontPackage)
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
            print ("=======     WeBASE-Front    starting .  Please check through the log file (default path:./{}/log/).    =======".format(frontPackage))
        else:
            print ("=======     WeBASE-Front    start fail. Please check through the log file (default path:./{}/log/).    =======".format(frontPackage))
            sys.exit(0)
    else:
        print ("=======     WeBASE-Front    start  fail. Please view log file (default path:./log/).    =======")
        sys.exit(0)
    print ("==============     WeBASE-Front     end...    ==============")
    print ("================================================================")
    return

def stopFront():
    os.chdir(currentDir)
    server_dir = currentDir + "/webase-front"
    if not os.path.exists(server_dir):
        print ("======= WeBASE-Front is not deploy. return! =======")
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
    print ("================================================================")
    print ("============== WeBASE-Sign install... ==============")
    os.chdir(currentDir)
    sign_version = getCommProperties("webase.sign.version")
    gitComm = "wget https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/{}/webase-sign.zip ".format(sign_version)
    pullSourceExtract(gitComm,"webase-sign")
    changeSignConfig()
    signDbConnect()
    startSign()
    return

def installDockerImage():
    print ("================================================================")
    print ("============== Download docker image from CDN... ==============")
    os.chdir(currentDir)
    image_version = getCommProperties("fisco.webase.docker.cdn.version")
    gitComm = "wget https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/{}/docker-fisco-webase.tar".format(image_version)
    pullDockerImage(gitComm,"docker-fisco-webase.tar","fiscoorg/fisco-webase")

    gitComm = "wget https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/{}/docker-fisco-webase-gm.tar".format(image_version)
    pullDockerImage(gitComm,"docker-fisco-webase-gm.tar","fiscoorg/fisco-webase")

    return

def startSign():
    print ("============== WeBASE-Sign  start...  ==============")
    os.chdir(currentDir)
    signPort = getCommProperties("sign.port")
    server_dir = currentDir + "/webase-sign"
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
            print ("======= WeBASE-Sign starting. Please check through the log file (default path:./webase-sign/log/). =======")
        else:
            print ("======= WeBASE-Sign start fail. Please check through the log file (default path:./webase-sign/log/). =======")
            sys.exit(0)
    else:
        print ("======= WeBASE-Sign start fail. Please view log file (default path:./log/).    =======")
        sys.exit(0)
    print ("============== WeBASE-Sign  end...    ==============")
    return

def stopSign():
    server_dir = currentDir + "/webase-sign"
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
            if frontEnable:
                log.info(" initFrontForMgr frontEnable {}".format(frontEnable))
                addFrontToDb()
                rest_get(url)
                print("= 100%")
                print ("==============  Init Front for Mgr end...     ==============")
                return
        if not frontEnable:
            print ("==============  Init Front for Mgr fail.      ==============")
            return
