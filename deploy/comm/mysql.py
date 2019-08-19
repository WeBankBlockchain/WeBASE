#!/usr/bin/env python3
# encoding: utf-8

from . import log as deployLog
import sys
import MySQLdb as mdb
from .utils import *

log = deployLog.getLocalLogger()

def dbConnect():
    # get properties
    mysql_ip = getCommProperties("mysql.ip")
    mysql_port = int(getCommProperties("mysql.port"))
    mysql_user = getCommProperties("mysql.user")
    mysql_password = getCommProperties("mysql.password")
    mysql_database = getCommProperties("mysql.database")

    try:
        # connect
        conn = mdb.connect(host=mysql_ip, port=mysql_port, user=mysql_user, passwd=mysql_password, charset='utf8')
        conn.autocommit(1)
        cursor = conn.cursor()
        
        # check db
        result = cursor.execute('show databases like "%s"' %mysql_database)
        drop_db = 'DROP DATABASE IF EXISTS {}'.format(mysql_database)
        create_db = 'CREATE DATABASE IF NOT EXISTS {}'.format(mysql_database)
        if result == 1:
            info = "n"
            if sys.version_info.major == 2:
                info = raw_input("WeBASE-Node-Manager数据库{}已经存在，是否删除重建？[y/n]:".format(mysql_database))
            else:
                info = input("WeBASE-Node-Manager数据库{}已经存在，是否删除重建？[y/n]:".format(mysql_database))
            if info == "y" or info == "Y":
                log.info(drop_db)
                cursor.execute(drop_db)
                log.info(create_db)
                cursor.execute(create_db)
        else:
            log.info(create_db)
            cursor.execute(create_db)
        cursor.close()
        conn.close()
    except:
        import traceback
        log.info(" mysql except {}".format(traceback.format_exc()))
        traceback.print_exc()
        sys.exit(0)
    
if __name__ == '__main__':
    pass
