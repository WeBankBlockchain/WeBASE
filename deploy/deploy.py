#!/usr/bin/python3
# encoding: utf-8

import sys

# check python version first
# check before import in case of avoiding error of mysql lib not found in comm.check package
if not sys.version_info.major == 3 and sys.version_info.minor >= 5:
    print("This script requires Python 3.5 or higher!")
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
    check:          check the environment
    installAll:     check the environment, deploy all server
    startAll:       check server port, start all server
    stopAll:        stop all server
    installWeBASE:  check the environment, deploy without FISCO-BCOS nodes and WeBASE-Front server.
    startWeBASE:    check server port, start all server deploy under visual deploy model
    stopWeBASE:     stop all server deploy under visual deploy model
    startNode:      start FISCO-BCOS nodes
    stopNode:       stop FISCO-BCOS nodes
    startWeb:       start WeBASE-Web server
    stopWeb:        stop WeBASE-Web server
    startManager:   start WeBASE-Node-Manager server
    stopManager:    stop WeBASE-Node-Manager server
    startFront:     start WeBASE-Front server
    stopFront:      stop WeBASE-Front server
    startSign:      start WeBASE-Sign server
    stopSign:       stop WeBASE-Sign server

Attention:
    1. Need to install python, jdk, mysql, MySQL-python or PyMySQL first
    2. Need to ensure a smooth network
    3. You need to install git, wget, nginx; if it is not installed, the installation script will automatically install these components, but this may fail.
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
