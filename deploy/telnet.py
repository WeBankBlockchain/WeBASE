#!/usr/bin/python3
# encoding: utf-8

import sys
from comm.utils import *

def do():
    deploy_ip = "127.0.0.1"
    web_port = int(getCommProperties("web.port"))
    mgr_port = int(getCommProperties("mgr.port"))
    front_port = int(getCommProperties("front.port"))
    
    telnet_web = net_if_used_no_msg(deploy_ip,web_port)
    telnet_mgr = net_if_used_no_msg(deploy_ip,mgr_port)
    telnet_front = net_if_used_no_msg(deploy_ip,front_port)
    print ("telnet_web:{} telnet_mgr:{} telnet_front:{}".format(telnet_web, telnet_mgr, telnet_front))
    
    if telnet_web and telnet_mgr and telnet_front:
        print ("deploy success.")
    else:
        print ("============= deploy log =============")
        deploy_log = doCmdIgnoreException("cat ./log/info.log")
        print (deploy_log["output"])
        if not telnet_web:
        	print ("============================ WeBASE-Web fail... ============================")
        	context = doCmdIgnoreException("cat ./webase-web/log/access.log")
        	print (context["output"])
        if not telnet_mgr:
        	print ("============================ WeBASE-Node-Manager fail... ============================")
        	print ("============= node-manager.out =============")
        	context1 = doCmdIgnoreException("cat ./webase-node-mgr/log/node-manager.out")
        	print (context1["output"])
        	print ("============= WeBASE-Node-Manager.log =============")
        	context2 = doCmdIgnoreException("cat ./webase-node-mgr/log/WeBASE-Node-Manager.log")
        	print (context2["output"])
        if not telnet_front:
        	print ("============================ WeBASE-Front fail... ============================")
        	print ("============= front.out =============")
        	context1 = doCmdIgnoreException("cat ./webase-front/log/front.out")
        	print (context1["output"])
        	print ("============= WeBASE-Front.log =============")
        	context2 = doCmdIgnoreException("cat ./webase-front/log/WeBASE-Front.log")
        	print (context2["output"])
        	print ("============= web3sdk.log =============")
        	context3 = doCmdIgnoreException("cat ./webase-front/log/web3sdk.log")
        	print (context3["output"])
        raise Exception("deploy fail.")
if __name__ == '__main__':
    do()
    pass