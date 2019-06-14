#!/usr/bin/python
# encoding: utf-8
import sys
import comm.check as commCheck
import comm.build as commBuild
def do():
    if len(sys.argv)==1:
        help()
        return
    param = sys.argv[1]
    if "startAll" == param:
        commCheck.do()
        commBuild.do()
    elif "stopAll" == param:
        commBuild.end()
    elif "startNode" == param:
        commCheck.checkNodePort()
        commBuild.startNode()
    elif "stopNode" == param:
        commBuild.stopNode()
    elif "startWeb" == param:
        commCheck.checkWebPort()
        commBuild.startWeb()
    elif "stopWeb" == param:
        commBuild.stopWeb()
    elif "startMgr" == param:
        commCheck.checkMgrPort()
        commBuild.startMgr()
    elif "stopMgr" == param:
        commBuild.stopMgr()
    elif "startFront" == param:
        commCheck.checkFrontPort()
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
    check : check the environment
    startAll : check the environment, deploy all server
    stopAll : stop all server
    startNode : start nodes
    stopNode : stop nodes
    startWeb : start web server
    stopWeb : stop web server
    startMgr : start mgr server
    stopMgr : stop mgr server
    startFront : start front server
    stopFront : stop front server
    
Attention:
    1. Need to install python2.7, jdk1.8.0_121+, mysql 5.6+, MySQL-python first
    2. Need to ensure a smooth network
    3. You need to install git, wget, nginx; if it is not installed, the installation script will automatically install these components, but this may fail.
    '''
    print helpMsg
    return

def paramError():
    print "Param error! Please check."
    print ""
    help()
    return

if __name__ == '__main__':
    do()
    pass