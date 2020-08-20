#!/usr/bin/env python3
# encoding: utf-8

from . import log as deployLog
import os
import sys
from .utils import *

log = deployLog.getLocalLogger()
checkDependent = ["git","openssl","curl","wget"]

def do():
    print ("================================================================"),
    webaseMsg = '''
              _    _     ______  ___  _____ _____ 
             | |  | |    | ___ \/ _ \/  ___|  ___|
             | |  | | ___| |_/ / /_\ \ `--.| |__  
             | |/\| |/ _ | ___ |  _  |`--. |  __| 
             \  /\  |  __| |_/ | | | /\__/ | |___ 
              \/  \/ \___\____/\_| |_\____/\____/  
    '''
    print (webaseMsg)
    print ("================================================================")
    print ("===================== envrionment check... =====================")
    installRequirements()
    checkNginx()
    checkJava()
    checkNodePort()
    checkWebPort()
    checkMgrPort()
    checkSignPort()
    checkFrontPort()
    checkSignDbConnect()
    checkMgrDbConnect()
    print ("===================== envrionment ready... =====================")
    print ("================================================================")

def visual_do():
    print ("================================================================"),
    webaseMsg = '''
              _    _     ______  ___  _____ _____ 
             | |  | |    | ___ \/ _ \/  ___|  ___|
             | |  | | ___| |_/ / /_\ \ `--.| |__  
             | |/\| |/ _ | ___ |  _  |`--. |  __| 
             \  /\  |  __| |_/ | | | /\__/ | |___ 
              \/  \/ \___\____/\_| |_\____/\____/  
    '''
    print (webaseMsg)
    print ("================================================================")
    print ("===================== envrionment check... =====================")
    installRequirements()
    checkDocker()
    checkNginx()
    checkJava()
    checkWebPort()
    checkMgrPort()
    checkSignIp()
    checkSignPort()
    checkSignDbConnect()
    checkMgrDbConnect()
    print ("===================== envrionment ready... =====================")
    print ("================================================================")

def checkPort():
    checkWebPort()
    checkMgrPort()
    checkSignPort()
    checkFrontPort()

def visualCheckPort():
    checkWebPort()
    checkMgrPort()
    checkSignPort()
    checkFrontPort()

def installRequirements():
   print ("================================================================")
   print ('===== check/install dependency of [git,openssl,curl,nginx] =====')
   for require in checkDependent:
      print ("check {}...".format(require))
      hasInstall = hasInstallServer(require)
      if not hasInstall:
        installByYum(require)
      print ("check finished sucessfully.")

def checkNginx():
    print ("check nginx...")
    require = "nginx"
    hasInstall = hasInstallServer(require)
    if not hasInstall:
        installByYum(require)
    print ("check finished sucessfully.")

def checkDocker():
    print ("check Docker...")
    require = "docker"
    hasInstall = hasInstallServer(require)
    if not hasInstall:
        doCmd("curl -s -L get.docker.com | bash")

    print("Try to start Docker...")
    doCmd("sudo systemctl start docker")
    print ("check finished sucessfully.")

def checkJava():
    print ("check java...")
    res_check = doCmdIgnoreException("java -version")
    if res_check["status"] != 0:
        print ("  error! java has not been installed or configured!")
        sys.exit(0)
    res_home = doCmd("echo $JAVA_HOME")
    if res_home["output"].strip() == "":
        print ("  error! JAVA_HOME has not been configured!")
        sys.exit(0)
    print ("check finished sucessfully.")
    return

def checkNodePort():
    if_exist_fisco = getCommProperties("if.exist.fisco")
    if if_exist_fisco == "yes":
        # checkExistedNodePort()
        return
    elif if_exist_fisco == "no":
        print ("check FISCO-BCOS node port...")
        checkNewNodePort()
        print ("check finished sucessfully.")
    else:
        print ("  error! param if.exist.fisco must be yes or no, current is {}. please check.".format(if_exist_fisco))
        sys.exit(0)

def checkExistedNodePort():
    listen_ip = getCommProperties("node.listenIp")
    node_rpcPort = int(getCommProperties("node.rpcPort"))
    node_p2pPort = int(getCommProperties("node.p2pPort"))
    node_channelPort = int(getCommProperties("node.channelPort"))
    res_rpcPort = net_if_used_no_msg(listen_ip,node_rpcPort)
    if not res_rpcPort:
        print ("  error! rpc port {} is not alive. please check.".format(node_rpcPort))
        sys.exit(0)
    res_p2pPort = net_if_used_no_msg(listen_ip,node_p2pPort)
    if not res_p2pPort:
        print ("  error! p2p port {} is not alive. please check.".format(node_p2pPort))
        sys.exit(0)
    res_channelPort = net_if_used_no_msg(listen_ip,node_channelPort)
    if not res_channelPort:
        print ("  error! channel port {} is not alive. please check.".format(node_channelPort))
        sys.exit(0)
    return
    
def checkNewNodePort():
    listen_ip = getCommProperties("node.listenIp")
    nodes = getCommProperties("node.counts")
    node_counts = 2
    if nodes != "nodeCounts":
        node_counts = int(nodes)
    node_rpcPort = int(getCommProperties("node.rpcPort"))
    node_p2pPort = int(getCommProperties("node.p2pPort"))
    node_channelPort = int(getCommProperties("node.channelPort"))
    for i in range(node_counts):
        res_rpcPort = net_if_used(listen_ip,node_rpcPort+i)
        if res_rpcPort:
            sys.exit(0)
        res_p2pPort = net_if_used(listen_ip,node_p2pPort+i)
        if res_p2pPort:
            sys.exit(0)
        res_channelPort = net_if_used(listen_ip,node_channelPort+i)
        if res_channelPort:
            sys.exit(0)
    return
    
def checkWebPort():
    print ("check WeBASE-Web port...")
    deploy_ip = "127.0.0.1"
    web_port = getCommProperties("web.port")
    res_web = net_if_used(deploy_ip,web_port)
    if res_web:
        sys.exit(0)
    print ("check finished sucessfully.")
    return
    
def checkMgrPort():
    print ("check WeBASE-Node-Manager port...")
    deploy_ip = "127.0.0.1"
    mgr_port = getCommProperties("mgr.port")
    res_mgr = net_if_used(deploy_ip,mgr_port)
    if res_mgr:
        sys.exit(0)
    print ("check finished sucessfully.")
    return
    
def checkFrontPort():
    print ("check WeBASE-Front port...")
    deploy_ip = "127.0.0.1"
    front_port = getCommProperties("front.port")

    if front_port is None:
        print ("======= WeBASE-Front is not deploy. return! =======")
        return

    res_front = net_if_used(deploy_ip,front_port)
    if res_front:
        sys.exit(0)
    print ("check finished sucessfully.")
    return

def checkSignPort():
    print ("check WeBASE-Sign port...")
    deploy_ip = "127.0.0.1"
    sign_port = getCommProperties("sign.port")
    res_sign = net_if_used(deploy_ip,sign_port)
    if res_sign:
        sys.exit(0)
    print ("check finished sucessfully.")
    return

def checkSignIp():
    print ("check WeBASE-Sign IP for visual deploy...")
    sign_ip = getCommProperties("sign.ip")
    if isBlank(sign_ip) or sign_ip == "127.0.0.1":
        print ("When using visual deploy, sign IP should be the external IP of this host, not 127.0.0.1.")
        sys.exit(0)
    print ("check finished sucessfully.")
    return

def isBlank (str):
    return not (str and str.strip())

def checkMgrDbConnect():
    print ("check database connection...")
    mysql_ip = getCommProperties("mysql.ip")
    mysql_port = getCommProperties("mysql.port")
    ifLink = do_telnet(mysql_ip,mysql_port)
    if not ifLink:
        print ('Mgr database ip:{} port:{} is disconnected, please confirm.'.format(mysql_ip, mysql_port))
        sys.exit(0)
    print ("check finished sucessfully.")
    return

def checkSignDbConnect():
    print ("check database connection...")
    mysql_ip = getCommProperties("sign.mysql.ip")
    mysql_port = getCommProperties("sign.mysql.port")
    ifLink = do_telnet(mysql_ip,mysql_port)
    if not ifLink:
        print ('Sign database ip:{} port:{} is disconnected, please confirm.'.format(mysql_ip, mysql_port))
        sys.exit(0)
    print ("check finished sucessfully.")
    return

def hasInstallServer(server):
    result = doCmdIgnoreException("which {}".format(server))
    if result["status"] == 0:
        return True
    else:
        return False

def installByYum(server):
    if isCentos():
        result = doCmdIgnoreException("sudo yum -y install {}".format(server))
        if result["status"] != 0:
            os.system("sudo yum -y install epel-release")
            os.system("sudo yum -y install python-pip")
            os.system("pip install requests")
            result = doCmd("sudo yum -y install {}".format(server))
    elif isSuse():
        os.system("sudo zypper install -y {}".format(server))
    elif isUbuntu():
        os.system("sudo apt-get install -y {}".format(server))
    else:
        print ("=========================================================================")
        print ('current system platform is not in target list(centos/redhat, ubuntu, suse')
        print ('======== please install dependency of [{}] on your own ========'.format(server))
        info = "n"
        if sys.version_info.major == 2:
            info = raw_input("Please check whether dependency of [{}] already installed, yes or not？[y/n]:".format(server))
        else:
            info = input("Please check whether dependency of [{}] already installed, yes or not？[y/n]:".format(server))
        if info == "y" or info == "Y":
            return
        else:
            raise Exception("error, not support this platform, only support centos/redhat, suse, ubuntu.")
    return

if __name__ == '__main__':
    pass
