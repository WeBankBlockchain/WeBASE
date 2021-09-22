#!/usr/bin/python3
# encoding: utf-8

import sys

# check python version first
# check before import in case of avoiding error of mysql lib not found in comm.check package
if not sys.version_info.major == 3 and sys.version_info.minor >= 6:
    print("This script requires Python 3.6 or higher!")
    print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)

import comm.check as commCheck
import comm.build as commBuild
import comm.global_var as gl

def do():
    if len(sys.argv)==1:
        help()
        return
    param = sys.argv[1]
    if "installAll" == param:
        gl.set_install_all()
        commCheck.do()
        commBuild.do()
    elif "startAll" == param:
        commCheck.checkPort()
        commBuild.start()
    elif "stopAll" == param:
        commBuild.end()
    elif "installWeBASE" == param:
        gl.set_visual_deploy()
        commCheck.visual_do()
        commBuild.visual_do()
    elif "startWeBASE" == param:
        commCheck.visualCheckPort()
        commBuild.visualStart()
    elif "stopWeBASE" == param:
        commBuild.visualEnd()
    elif "installDockerAll" == param:
        commCheck.docker_do()
        commBuild.docker_do()
    elif "startDockerAll" == param:
        commCheck.checkPort()
        commBuild.dockerStartAll()
    elif "stopDockerAll" == param:
        commBuild.dockerEndAll()
    elif "pullDockerAll" == param:
        commBuild.dockerPull()
    elif "startDocker" == param:
        commCheck.checkPort()
        commBuild.dockerStart()
    elif "stopDocker" == param:
        commBuild.dockerEnd()
    elif "startNode" == param:
        commBuild.startNode()
    elif "stopNode" == param:
        commBuild.stopNode()
    elif "startWeb" == param:
        commBuild.startWeb()
    elif "stopWeb" == param:
        commBuild.stopWeb()
    elif "startManager" == param:
        commBuild.startManager()
    elif "stopManager" == param:
        commBuild.stopManager()
    elif "startFront" == param:
        commBuild.startFront()
    elif "stopFront" == param:
        commBuild.stopFront()
    elif "startSign" == param:
        commBuild.startSign()
    elif "stopSign" == param:
        commBuild.stopSign()
    elif "check"== param:
        commCheck.do()
    elif "help"== param:
        help()
    else:
        paramError()
    return

def help():
    helpMsg = '''
Usage: python deploy [Parameter]

Parameter:
    check:          check the environment [one-click mode]
    installAll:     check the environment, deploy FISCO-BCOS and all service [one-click mode] 
    startAll:       check service port, start all service [one-click mode] 
    stopAll:        stop all service [one-click mode] 
    installWeBASE:  check the environment, deploy without FISCO-BCOS nodes and WeBASE-Front service [visual mode] 
    startWeBASE:    check service port, start all service deploy under visual deploy model [visual mode] 
    stopWeBASE:     stop all service deploy under visual deploy model [visual mode] 
    startNode:      start FISCO-BCOS nodes [one-click mode or docker mode]
    stopNode:       stop FISCO-BCOS nodes [one-click mode or docker mode]
    startWeb:       start WeBASE-Web service [one-click mode or visual mode]
    stopWeb:        stop WeBASE-Web service [one-click mode or visual mode]
    startManager:   start WeBASE-Node-Manager service [one-click mode or visual mode]
    stopManager:    stop WeBASE-Node-Manager service [one-click mode or visual mode]
    startFront:     start WeBASE-Front service [one-click mode]
    stopFront:      stop WeBASE-Front service [one-click mode]
    startSign:      start WeBASE-Sign service [one-click mode or visual mode]
    stopSign:       stop WeBASE-Sign service [one-click mode or visual mode]
    installDockerAll    check dependency, deploy FISCO-BCOS nodes and all service, start by docker
    startDockerAll      check docker container, start FISCO-BCOS nodes and all service by docker
    stopDockerAll       stop FISCO-BCOS nodes and all service in docker
    pullDockerAll       pull FISCO-BCOS, WeBASE and mysql images from dockerhub
    startDocker         check docker container, start all webase service by docker
    stopDocker          stop all webase service in docker

Attention:
    1. Need to install python3.6, jdk, mysql, PyMySQL first
    2. Need to ensure a smooth network
    3. You need to install git,openssl,curl,wget,nginx,dos2unix; if it is not installed, the installation script will automatically install these components, but this may fail.
    '''
    print (helpMsg)
    return

def paramError():
    print ("")
    print ("Param error! Please check.")
    help()
    return

if __name__ == '__main__':
    do()
    pass
