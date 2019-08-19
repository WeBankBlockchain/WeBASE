#!/usr/bin/python3
# encoding: utf-8

import sys
import comm.check as commCheck
import comm.build as commBuild
def do():
    if len(sys.argv)==1:
        help()
        return
    param = sys.argv[1]
    if "installAll" == param:
        commCheck.do()
        commBuild.do()
    elif "stopAll" == param:
        commBuild.end()
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
    check:        check the environment
    installAll:   check the environment, deploy all server
    stopAll:      stop all server
    startNode:    start FISCO-BCOS nodes
    stopNode:     stop FISCO-BCOS nodes
    startWeb:     start WeBASE-Web server
    stopWeb:      stop WeBASE-Web server
    startManager: start WeBASE-Node-Manager server
    stopManager:  stop WeBASE-Node-Manager server
    startFront:   start WeBASE-Front server
    stopFront:    stop WeBASE-Front server
    
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