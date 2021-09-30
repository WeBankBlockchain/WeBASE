#!/usr/bin/env python3
# encoding: utf-8

import os
import sys
import comm.global_var as gl

try:
    import ConfigParser
except:
    try:
        import configparser as ConfigParser
    except:
        from six.moves import configparser as ConfigParser
if sys.version_info.major == 2:
    import commands
else:
    import subprocess
from . import log as deployLog
import socket
import fcntl
import struct
import telnetlib
import platform
import shutil
import json
from urllib import request
from distutils.dir_util import copy_tree
# support timeout
import signal
import subprocess

log = deployLog.getLocalLogger()
platformStr = platform.platform()
unameStr = platform.uname()[1]
versionStr = platform.uname()[3]

def getIpAddress(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def getLocalIp():
    return getIpAddress("eth0")

def net_if_used(ip,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        result=s.connect_ex((ip, int(port)))
        if result==0:
            print ("  error! port {} has been used. please check.".format(port))
            return True
        else:
            return False
    finally:
        s.close()

def net_if_used_no_msg(ip,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        result=s.connect_ex((ip, int(port)))
        if result==0:
            return True
        else:
            return False
    finally:
        s.close()

def isUbuntu():
    return platformStr.lower().find("ubuntu") > -1 or unameStr.lower().find("ubuntu") > -1 or versionStr.lower().find("ubuntu") > -1

def isCentos():
    # support redhat
    return platformStr.lower().find("centos") > -1 or unameStr.lower().find("centos") > -1 or unameStr.lower().find("redhat") > -1 or versionStr.lower().find("centos") > -1

def isSuse():
    return platformStr.lower().find("suse") > -1  or unameStr.lower().find("suse") > -1 or versionStr.lower().find("suse") > -1

def getBaseDir():
    cwd = os.getcwd()
    log.info("  os.getcwd() is {}".format(cwd))
    path = os.path.abspath(os.path.join(os.getcwd(), ".."))
    return path

def getCurrentBaseDir():
    cwd = os.getcwd()
    log.info("  os.getcwd() is {}".format(cwd))
    path = os.path.abspath(os.path.join(os.getcwd(), "."))
    return path

def copytree(src, dst):
    copy_tree(src,dst)
    return

def doCmd(cmd):
    log.info(" execute cmd  start ,cmd : {}".format(cmd))
    result = dict()
    if sys.version_info.major == 2:
        (status, output) = commands.getstatusoutput(cmd)
    else:
        (status, output) = subprocess.getstatusoutput(cmd)
    result["status"] = status
    result["output"] = output
    log.info(" execute cmd  end ,cmd : {},status :{} , output: {}".format(cmd,status,output))
    if (0 != status):
        raise Exception("execute cmd  error ,cmd : {}, status is {} ,output is {}".format(cmd,status, output))
    return result

def doCmdIgnoreException(cmd):
    log.info(" execute cmd  start ,cmd : {}".format(cmd))
    result = dict()
    if sys.version_info.major == 2:
        (status, output) = commands.getstatusoutput(cmd)
    else:
        (status, output) = subprocess.getstatusoutput(cmd)
    result["status"] = status
    result["output"] = output
    log.info(" execute cmd  end ,cmd : {},status :{} , output: {}".format(cmd, status, output))
    return result


def doCmdTimeout(cmd_string, timeout=20):
    log.info(" execute cmd  start, cmd: {}, timeout: {}".format(cmd_string, timeout))
    p = subprocess.Popen(cmd_string, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True, close_fds=True, start_new_session=True)
    format = 'utf-8'
    try:
        (msg, errs) = p.communicate(timeout=timeout)
        ret_code = p.poll()
        if ret_code:
            status = 1
            output = "[Error]Called Error ： " + str(msg.decode(format))
        else:
            status = 0
            output = str(msg.decode(format))
    except subprocess.TimeoutExpired:
        # 注意：不能只使用p.kill和p.terminate，无法杀干净所有的子进程，需要使用os.killpg
        p.kill()
        p.terminate()
        os.killpg(p.pid, signal.SIGTERM)
        # 注意：如果开启下面这两行的话，会等到执行完成才报超时错误，但是可以输出执行结果
        # (outs, errs) = p.communicate()
        # print(outs.decode('utf-8'))
        status = 0
        log.info("[ERROR]Timeout Error : Command '" + cmd_string + "' timed out after " + str(timeout) + " seconds")
        output = "timeout"
    except Exception as e:
        status = 1
        output = "[ERROR]Unknown Error : " + str(e)
    
    result = dict()
    result["status"] = status
    result["output"] = output
    log.info(" execute cmd  end ,cmd : {},status :{} , output: {}".format(cmd_string, status, output))
    if (0 != status):
        raise Exception("execute cmd  error ,cmd : {}, status is {} ,output is {}".format(cmd_string, status, output))
    return result

 

def getCommProperties(paramsKey):
    current_dir = getCurrentBaseDir()
    cf = ConfigParser.ConfigParser()
    propertiesDir =current_dir + '/' + gl.get_file()
    cf.read(propertiesDir)
    log.info(" commProperties is {} ".format(propertiesDir))
    cf.sections()
    value = cf.get('common', paramsKey,fallback=None)
    return value

def replaceConf(fileName,oldStr,newStr):
    if not os.path.isfile(fileName):
        print ("{} is not a file ".format(fileName))
        return
    oldData =""
    with open(fileName, "r") as f:
        for line in f:
            if oldStr in line:
                line = line.replace(oldStr, newStr)
            oldData += line
    with open(fileName, "w") as f:
        f.write(oldData)
    return

def replaceConfDir(filePath,oldStr,newStr):
    if not os.path.isdir(filePath):
        print ("{} is not a dir ".format(filePath))
        return
    for root, dirs, files in os.walk(filePath):
        for file in files:
            replaceConf(os.path.join(root,file),oldStr,newStr)
    return

def copyFiles(sourceDir, targetDir):
    log.info(" copyFiles sourceDir: {} ".format(sourceDir))
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)
        if os.path.isfile(sourceF):
            # check dir
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            # copy file
            shutil.copy(sourceF,targetF)
        # check sub folder
        if os.path.isdir(sourceF):
            copyFiles(sourceF, targetF)

def do_telnet(host,port):
    try:
        tn = telnetlib.Telnet(host, port, timeout=5)
        tn.close()
    except:
        return False
    return True

# required docker command not need sudo
def pullDockerImage(gitComm,fileName,repo_name):
    if not os.path.exists("{}/{}".format(getCurrentBaseDir(),fileName)):
        print (gitComm)
        # get tar file from this gitComm command
        os.system(gitComm)
    else:
        info = "n"
        if sys.version_info.major == 2:
            info = raw_input("{} already exists. Do you want to re-download and overwrite it?[y/n]:".format(fileName))
        else:
            info = input("{} already exists. Do you want to re-download and overwrite it?[y/n]:".format(fileName))
        if info == "y" or info == "Y":
            doCmd("rm -rf {}".format(fileName))
            print (gitComm)
            # get tar file from this gitComm command
            os.system(gitComm)

    doCmd("docker load -i {}".format(fileName))

    result = doCmd("docker image ls {} | wc -l".format(repo_name))
    print ("Uzip image result {} ".format(result))
    if int(result["output"]) <= 1 :
        print ("Unzip docker image from file {} failed!".format(fileName))
        sys.exit(0)

# repo_name ex: fiscoorg/fiscobcos, webasepro/webase-front:v1.5.3
def checkDockerImageExist(repo_name):
    result = doCmd("docker image ls {} | wc -l".format(repo_name))
    log.info("local image result {} ".format(result))
    if int(result["output"]) <= 1 :
        print ("Local docker image {} not exist!".format(repo_name))
        return False
    else:
        return True

def pullSourceExtract(gitComm,fileName):
    if not os.path.exists("{}/{}.zip".format(getCurrentBaseDir(),fileName)):
        print (gitComm)
        os.system(gitComm)
    else:
        info = "n"
        if sys.version_info.major == 2:
            info = raw_input("{}.zip already exists. Do you want to re-download and overwrite it?[y/n]:".format(fileName))
        else:
            info = input("{}.zip already exists. Do you want to re-download and overwrite it?[y/n]:".format(fileName))
        if info == "y" or info == "Y":
            doCmd("rm -rf {}.zip".format(fileName))
            doCmd("rm -rf {}".format(fileName))
            print (gitComm)
            os.system(gitComm)
    if not os.path.exists("{}/{}".format(getCurrentBaseDir(),fileName)):
        doCmd("unzip -o {}.zip".format(fileName))
        if not os.path.exists("{}/{}".format(getCurrentBaseDir(),fileName)):
            print ("{}.zip extract failed!".format(fileName))
            sys.exit(0)
    else:
        info1 = "n"
        if sys.version_info.major == 2:
            info1 = raw_input("directory '{}' is not empty. Do you want delete and re-unzip {}.zip?[y/n]:".format(fileName,fileName))
        else:
            info1 = input("directory '{}' is not empty. Do you want delete and re-unzip {}.zip?[y/n]:".format(fileName,fileName))
        if info1 == "y" or info1 == "Y":
            doCmd("rm -rf {}".format(fileName))
            doCmd("unzip -o {}.zip".format(fileName))
            if not os.path.exists("{}/{}".format(getCurrentBaseDir(),fileName)):
                print ("{}.zip extract failed!".format(fileName))
                sys.exit(0)

def checkFileName(dir,fileName):
    Files=os.listdir(dir)
    for k in range(len(Files)):
        Files[k]=os.path.splitext(Files[k])[0]
    fileName = fileName + ".mv"
    if fileName in Files:
        return True
    else:
        return False

def checkPathExists(pathName):
    if os.path.exists(pathName):
        return True
    else:
        print ("======={} is not exists.=======".format(pathName))
        return False

def get_str_btw(s, f, b):
    par = s.partition(f)
    return (par[2].partition(b))[0][:]
    
def rest_get(url):
    log.info("rest_get url: {}".format(url))
    try:
        res = request.urlopen(url)
        log.info("rest_get success: {}".format(res.read()))
        return res
    except:
        log.error("rest_get fail: {}".format(sys.exc_info()))
        return ''
    
def rest_post(url,data):
    log.info("rest_post url: {}, data:{}".format(url, data))
    raw_params = json.dumps(data)
    params = bytes(raw_params, 'utf8')
    headers = {'Accept-Charset': 'utf-8', 'Content-Type': 'application/json'}
    try:
        req = request.Request(url=url, data=params, headers=headers, method='POST')
        res = request.urlopen(req).read()
        res_dict = json.loads(res)
        log.info("rest_post success: {}".format(res_dict))
        return res_dict
    except:
        log.error("rest_post fail: {}".format(sys.exc_info()))
        return ''

def rest_getClientVersion(chainRpcUrl):
    data={"jsonrpc":"2.0","method":"getClientVersion","params":[],"id":1}
    resJson = rest_post(chainRpcUrl,data)
    result = resJson['result']
    log.info("rest_getClientVersion result: {}".format(result))
    return result

if __name__ == '__main__':
    print(getIpAddress("eth0"))
    pass
