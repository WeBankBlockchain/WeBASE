#!/usr/bin/env python3
# encoding: utf-8

import os
import sys
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
from distutils.dir_util import copy_tree

log = deployLog.getLocalLogger()
platformStr = platform.platform()

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
    return platformStr.lower().find("ubuntu") > -1

def isCentos():
    return platformStr.lower().find("centos") > -1

def isSuse():
    return platformStr.lower().find("suse") > -1

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

def getCommProperties(paramsKey):
    current_dir = getCurrentBaseDir()
    cf = ConfigParser.ConfigParser()
    propertiesDir =current_dir+"/common.properties"
    cf.read(propertiesDir)
    log.info(" commProperties is {} ".format(propertiesDir))
    cf.sections()
    value = cf.get('common', paramsKey)
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
            
def pullSourceExtract(gitComm,fileName):
    if not os.path.exists("{}/{}.zip".format(getCurrentBaseDir(),fileName)):
        print (gitComm)
        os.system(gitComm)
    else:
        info = "n"
        if sys.version_info.major == 2:
            info = raw_input("{}.zip编译包已经存在。是否重新下载？[y/n]:".format(fileName))
        else:
            info = input("{}.zip编译包已经存在。是否重新下载？[y/n]:".format(fileName))
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
            info1 = raw_input("{}.zip编译包已经解压。是否重新解压？[y/n]:".format(fileName))
        else:
            info1 = input("{}.zip编译包已经解压。是否重新解压？[y/n]:".format(fileName))
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
        
def get_str_btw(s, f, b):
    par = s.partition(f)
    return (par[2].partition(b))[0][:]

if __name__ == '__main__':
    print(getIpAddress("eth0"))
    pass