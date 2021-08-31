#!/usr/bin/env python3
# encoding: utf-8

from . import log as deployLog
import os
import sys
from .utils import *
from .mysql import *
import re
#import psutil

log = deployLog.getLocalLogger()
checkDependent = ["git","openssl","curl","wget","dos2unix"]
# memery(B) and cpu(core counts logical)
# mem=psutil.virtual_memory()
# cpuCore=psutil.cpu_count()

def do():
    print ("============================================================"),
    webaseMsg = '''
              _    _     ______  ___  _____ _____ 
             | |  | |    | ___ \/ _ \/  ___|  ___|
             | |  | | ___| |_/ / /_\ \ `--.| |__  
             | |/\| |/ _ | ___ |  _  |`--. |  __| 
             \  /\  |  __| |_/ | | | /\__/ | |___ 
              \/  \/ \___\____/\_| |_\____/\____/  
    '''
    print (webaseMsg)
    print ("============================================================")
    print ("==============      checking envrionment      ==============")
    installRequirements()
    checkConfigVersion()
    checkMemAndCpu()
    checkNginx()
    checkJava()
    checkNodePort()
    checkWebPort()
    checkMgrPort()
    checkSignPort()
    checkFrontPort()
    checkMgrDbConnect()
    checkSignDbConnect()
    checkMgrDbAuthorized()
    checkSignDbAuthorized()
    checkMgrDbVersion()
    checkSignDbVersion()
    checkExitedChainInfo()
    print ("==============      envrionment available     ==============")
    print ("============================================================")

def visual_do():
    print ("============================================================"),
    webaseMsg = '''
              _    _     ______  ___  _____ _____ 
             | |  | |    | ___ \/ _ \/  ___|  ___|
             | |  | | ___| |_/ / /_\ \ `--.| |__  
             | |/\| |/ _ | ___ |  _  |`--. |  __| 
             \  /\  |  __| |_/ | | | /\__/ | |___ 
              \/  \/ \___\____/\_| |_\____/\____/  
    '''
    print (webaseMsg)
    print ("============================================================")
    print ("==============      checking envrionment      ==============")
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
    checkMgrDbAuthorized()
    checkSignDbAuthorized()
    checkMgrDbVersion()
    checkSignDbVersion()
    print ("==============      envrionment available     ==============")
    print ("============================================================")

def docker_do():
    print ("============================================================"),
    webaseMsg = '''
              _    _     ______  ___  _____ _____ 
             | |  | |    | ___ \/ _ \/  ___|  ___|
             | |  | | ___| |_/ / /_\ \ `--.| |__  
             | |/\| |/ _ | ___ |  _  |`--. |  __| 
             \  /\  |  __| |_/ | | | /\__/ | |___ 
              \/  \/ \___\____/\_| |_\____/\____/  
    '''
    print (webaseMsg)
    print ("============================================================")
    print ("==============      checking envrionment      ==============")
    installRequirements()
    checkDocker()
    checkDockerCompose()
    checkConfigVersion()
    checkMemAndCpu()
    checkNodePort()
    checkWebPort()
    checkMgrPort()
    checkSignPort()
    checkFrontPort()
    # if not docker mysql, check connect, auth, version
    dockerCheckDb()
    checkExitedChainInfo()
    print ("==============      envrionment available     ==============")
    print ("============================================================")
    

def checkPort():
    print ("==============      checking    port          ==============")
    checkWebPort()
    checkMgrPort()
    checkSignPort()
    checkFrontPort()
    print ("==============        port    available       ==============")

def visualCheckPort():
    print ("==============      checking    port          ==============")
    checkWebPort()
    checkMgrPort()
    checkSignPort()
    print ("==============        port    available       ==============")

def installRequirements():
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

def checkDockerCompose():
    print ("check docker-compose...")
    require = "docker-compose"
    hasInstall = hasInstallServer(require)
    if not hasInstall:
        print ("  error! [{}] has not been installed or configured!".format(require))
        sys.exit(0)
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
        print ("============================================================")
        print ('current system platform is not in target list(centos/redhat, ubuntu, suse')
        print ('===== please install dependency of [{}] on your own ====='.format(server))
        info = "n"
        if sys.version_info.major == 2:
            info = raw_input("Please check whether dependency of [{}] already installed, yes or not?[y/n]:".format(server))
        else:
            info = input("Please check whether dependency of [{}] already installed, yes or not?[y/n]:".format(server))
        if info == "y" or info == "Y":
            return
        else:
            raise Exception("error, not support this platform, only support centos/redhat, suse, ubuntu.")
    return

# update every version
# check fisco version and webase-front version
def checkConfigVersion():
    existChain = getCommProperties("if.exist.fisco")
    if (existChain == 'no'):
        fisco_ver_str = getCommProperties("fisco.version")
        webase_front_ver_str = getCommProperties("webase.front.version")
        print ("check config webase {} and fisco version {}...".format(webase_front_ver_str, fisco_ver_str))
        # check from common.properties
        checkVersionUtil(fisco_ver_str,webase_front_ver_str)
        print ('check finished sucessfully.')

def checkVersionUtil(fisco_ver_str,webase_front_ver_str):
    log.info("checkVersionUtil webase: {} and fisco version: {}".format(webase_front_ver_str, fisco_ver_str))
    fisco_version_int = int(re.findall("\d+", fisco_ver_str)[0]) * 100 + int(re.findall("\d+", fisco_ver_str)[1]) * 10 + int(re.findall("\d+", fisco_ver_str)[2]) * 1
    # webase-front version greater or equal with other webase version
    webase_front_version_int = int(re.findall("\d+", webase_front_ver_str)[0]) * 100 + int(re.findall("\d+", webase_front_ver_str)[1]) * 10 + int(re.findall("\d+", webase_front_ver_str)[2]) * 1
    log.info("checkVersionUtil int webase: {} and fisco version: {}".format(webase_front_version_int, fisco_version_int))
    flag=False
    # require if webase <= 1.3.2, fisco < 2.5.0
    if ( webase_front_version_int <= 132 and fisco_version_int >= 250 ):
        flag=True
    # require if webase >= 1.3.1(dynamic group), fisco >= 2.4.1
    if ( webase_front_version_int >= 131 and fisco_version_int < 241 ):
        flag=True

    # if version conflicts, exit
    if (flag):
        raise Exception ('[ERROR]WeBASE of version {} not support FISCO of version {}, please check WeBASE version description or ChangeLog for detail!'.format(webase_front_ver_str, fisco_ver_str))
    else:
        return

def checkMemAndCpu():
    print ("check host free memory and cpu core...")
    # result format: {'status': 0, 'output': '151.895'}
    # get free memory(M)
    memFree=doCmd("awk '($1 == \"MemFree:\"){print $2/1024}' /proc/meminfo 2>&1")
    # get cpu core num
    # cpuCore=doCmd("cat /proc/cpuinfo | grep processor | wc -l 2>&1")
    if (int(memFree.get("status")) != 0):
        raise Exception('Get memory or cpu core fail memFree:{}'.format(memFree))
    memFreeStr=memFree.get("output").split(".", 1)[0]
    memFreeInt=int(memFreeStr)

    existed_chain = getCommProperties("if.exist.fisco")
    # if existed chain, only need memory for webase
    if (existed_chain == 'yes'):
        if (memFreeInt <= 2047):
            print ('[WARN]Free memory {}(M) may be NOT ENOUGH for webase'.format(memFreeInt))
            print ("[WARN]Recommend webase with 2G memory at least. ")
        else:
            print ('check finished sucessfully.')
            return        
    # else not existed chain
    fisco_count_str = getCommProperties("node.counts")
    fisco_count = 2
    if (fisco_count_str != 'nodeCounts'):
        fisco_count = int(fisco_count_str)
    # check 2 nodes, 4 nodes, more nodes memory free rate/cpu require
    flag=False
    if (fisco_count <= 2):
        if (memFreeInt <= 2047):
            flag=True
    if (fisco_count >= 4):
        if (memFreeInt <= 4095):
            flag=True
    if (flag):
        print ('[WARN]Free memory {}(M) may be NOT ENOUGH for node count [{}] and webase'.format(memFreeInt, fisco_count))
        print ("[WARN]Recommend webase with 2G memory at least, and one node equipped with one core of CPU and 1G memory(linear increase with node count). ")
    else:
        print ('check finished sucessfully.')
        return

def checkExitedChainInfo():
    existChain = getCommProperties("if.exist.fisco")
    if (existChain == 'yes'):
        print ("check exited chain info...")
        
        listenIp = getCommProperties("node.listenIp")
        rpcPort = getCommProperties("node.rpcPort")
        chainRpcUrl = "http://{}:{}".format(listenIp,rpcPort)
        
        # check chain connect
        checkExistChainConnect()
        # request chain
        clientVersion=rest_getClientVersion(chainRpcUrl)
        # handle result
        fiscoVersion=clientVersion['FISCO-BCOS Version']
        log.info("fiscoVersion: {}".format(fiscoVersion))
        # check encrypt type
        checkEncryptType(fiscoVersion)
        # check version
        checkExitedChainVersion(fiscoVersion)
        
        print ('check exited chain info sucessfully.')
    else:
        return

def checkEncryptType(fiscoVersion):
    print ("check encrypt type...")
    encryptType = getCommProperties("encrypt.type")
    isGuomi="gm" in fiscoVersion
    if (isGuomi and encryptType != '1'):
        raise Exception("config's encryptType CONFLICTS with existed [guomi] chain")
    elif ((isGuomi == False) and encryptType == '1'):
        raise Exception("config's encryptType CONFLICTS with existed [ecdsa] chain")
    else:
        print ('check encrypt type finished.')
        return
    print ('check encrypt type finished.')

def checkExitedChainVersion(fisco_ver_str):
    print ("check version...")
    webase_front_ver_str = getCommProperties("webase.front.version")
    checkVersionUtil(fisco_ver_str,webase_front_ver_str)
    print ("check version finished.")

def checkExistChainConnect():
    print ("check connection...")
    listenIp = getCommProperties("node.listenIp")
    rpcPort = getCommProperties("node.rpcPort")
    ifLink = do_telnet(listenIp,rpcPort)
    if not ifLink:
        print ('Exist chain listen ip:{} port:{} is disconnected, please confirm.'.format(listenIp, rpcPort))
        sys.exit(0)
    print ("check connection finished.")
    return

def dockerCheckDb():
    print ("==============      checking    mysql           ==============")
    docker_mysql = int(getCommProperties("docker.mysql"))
    # use docker and also use docker mysql
    if docker_mysql == 0:
        checkMgrDbConnect()
        checkSignDbConnect()
        checkMgrDbAuthorized()
        checkSignDbAuthorized()
        checkMgrDbVersion()
        checkSignDbVersion()
    else: 
        print ("use [mysql in docker], skip check mysql")
    print ("==============        mysql    available       ==============")

if __name__ == '__main__':
    pass
