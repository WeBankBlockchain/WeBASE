#!/usr/bin/env python
# encoding: utf-8

import log as deployLog
import sys
from utils import *

log = deployLog.getLogger()
checkDependent = ["git","openssl","curl","nginx"]

def do():
    print "===================== envrionment check... ====================="
    installRequirements()
    checkSoft()
    checkNodePort()
    checkWebPort()
    checkMgrPort()
    checkFrontPort()
    checkDbConnect()
    print "===================== envrionment ready... ====================="

def installRequirements():
    for require in checkDependent:
        print "check {}...".format(require)
        hasInstall = hasInstallServer(require)
        if not hasInstall:
            installByYum(require)
        print "check finished Sucessfully."
    return

def checkSoft():
    print "check java..."
    res1 = doCmdIgnoreException("java -version")
    if res1["status"] != 0:
        print "  error! java is not install or configure!"
        sys.exit(0)
    print "check finished Sucessfully."
    return
    
def checkNodePort():
    print "check node port..."
    deploy_ip = "127.0.0.1"
    nodes = getCommProperties("node.counts")
    node_counts = 2
    if nodes is not "nodeCounts":
        node_counts = int(nodes)
    node_rpcPort = int(getCommProperties("node.rpcPort"))
    node_p2pPort = int(getCommProperties("node.p2pPort"))
    node_channelPort = int(getCommProperties("node.channelPort"))
    for i in range(node_counts):
        res_rpcPort = net_if_used("127.0.0.1",node_rpcPort+i)
        if res_rpcPort:
            sys.exit(0)
        res_p2pPort = net_if_used("127.0.0.1",node_p2pPort+i)
        if res_p2pPort:
            sys.exit(0)
        res_channelPort = net_if_used("127.0.0.1",node_channelPort+i)
        if res_channelPort:
            sys.exit(0)
    print "check finished Sucessfully."
    return
    
def checkWebPort():
    print "check web port..."
    deploy_ip = "127.0.0.1"
    web_port = getCommProperties("web.port")
    res_web = net_if_used(deploy_ip,web_port)
    if res_web:
        sys.exit(0)
    print "check finished Sucessfully."
    return
    
def checkMgrPort():
    print "check mgr port..."
    deploy_ip = "127.0.0.1"
    mgr_port = getCommProperties("mgr.port")
    res_mgr = net_if_used(deploy_ip,mgr_port)
    if res_mgr:
        sys.exit(0)
    print "check finished Sucessfully."
    return
    
def checkFrontPort():
    print "check front port..."
    deploy_ip = "127.0.0.1"
    front_port = getCommProperties("front.port")
    res_front = net_if_used(deploy_ip,front_port)
    if res_front:
        sys.exit(0)
    print "check finished Sucessfully."
    return
    
def checkDbConnect():
    print "check db connection..."
    mysql_ip = getCommProperties("mysql.ip")
    mysql_port = getCommProperties("mysql.port")
    ifLink = do_telnet(mysql_ip,mysql_port)
    if not ifLink:
        print 'The database ip:{} port:{} is disconnected, please confirm.'.format(mysql_ip, mysql_port)
        sys.exit(0)
    print "check finished Sucessfully."
    return
        
def checkSdkDir():
    print "checking sdk dir"
    nodeDir = getCommProperties("node.sdkDir")
    if not os.path.exists(nodeDir):
        print "{} is not exists".format(nodeDir)
        return

def hasInstallServer(server):
    result = doCmdIgnoreException("which {}".format(server))
    if result["status"] == 0:
        return True
    else:
        return False

def installByYum(server):
    if isCentos():
        result = doCmd("sudo yum -y install {}".format(server))
        if result["status"] !=0:
            os.system("yum install epel-release")
            os.system("sudo yum install python-pip")
            os.system("pip install --upgrade pip")
            os.system("pip install requests")
            result = doCmd("yum install {}".format(server))
    elif isSuse():
        os.system("sudo zypper install  -y {}".format(server))
    elif isUbuntu():
        os.system("sudo apt-get install  -y {}".format(server))
    else:
        raise Exception("error,not support this platform,only support centos,suse,ubuntu.")
    return

if __name__ == '__main__':
    pass
