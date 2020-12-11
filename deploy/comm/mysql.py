#!/usr/bin/env python3
# encoding: utf-8

from . import log as deployLog
import sys
import MySQLdb as mdb
from .utils import *

log = deployLog.getLocalLogger()

def addFrontToDb():
    # get properties
    mysql_ip = getCommProperties("mysql.ip")
    mysql_port = int(getCommProperties("mysql.port"))
    mysql_user = getCommProperties("mysql.user")
    mysql_password = getCommProperties("mysql.password")
    mysql_database = getCommProperties("mysql.database")
    front_org = getCommProperties("front.org")
    front_port = getCommProperties("front.port")
    fisco_version = getCommProperties("fisco.version")

    try:
        # connect
        conn = mdb.connect(host=mysql_ip, port=mysql_port, user=mysql_user, passwd=mysql_password, database=mysql_database, charset='utf8')
        conn.autocommit(1)
        cursor = conn.cursor()
        
        # add db
        add_db = "INSERT INTO tb_front (node_id,front_ip,front_port,agency,client_version, create_time, modify_time) \
                  VALUES ('init','127.0.0.1',%s,\'%s\',\'%s\', NOW(),NOW())" % \
                  (front_port, front_org, fisco_version)
        log.info(add_db)
        cursor.execute(add_db)
        conn.commit()
        cursor.close()
        conn.close()
    except:
        import traceback
        log.info(" mysql except {}".format(traceback.format_exc()))
        traceback.print_exc()
        sys.exit(0)

def dbConnect():
    # return whether to init tables
    whether_init = True
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
                info = raw_input("WeBASE-Node-Manager database {} already exists. Do you want drop and recreate it?[y/n]:".format(mysql_database))
            else:
                info = input("WeBASE-Node-Manager database {} already exists. Do you want drop and recreate it?[y/n]:".format(mysql_database))
            if info == "y" or info == "Y":
                log.info(drop_db)
                cursor.execute(drop_db)
                log.info(create_db)
                cursor.execute(create_db)
            # if not rebuild database, no need to re-init tables of database
            else:
                whether_init = False
        else:
            log.info(create_db)
            cursor.execute(create_db)
        cursor.close()
        conn.close()
        return whether_init
    except:
        import traceback
        log.info(" mysql except {}".format(traceback.format_exc()))
        traceback.print_exc()
        sys.exit(0)

def signDbConnect():
    # get properties
    mysql_ip = getCommProperties("sign.mysql.ip")
    mysql_port = int(getCommProperties("sign.mysql.port"))
    mysql_user = getCommProperties("sign.mysql.user")
    mysql_password = getCommProperties("sign.mysql.password")
    mysql_database = getCommProperties("sign.mysql.database")

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
                info = raw_input("WeBASE-Sign database {} already exists. Do you want drop and recreate it?[y/n]:".format(mysql_database))
            else:
                info = input("WeBASE-Sign database {} already exists. Do you want drop and recreate it?[y/n]:".format(mysql_database))
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
    

def checkMgrDbAuthorized():
    log.info("check mgr database user/password...")
    # get properties
    mysql_ip = getCommProperties("mysql.ip")
    mysql_port = int(getCommProperties("mysql.port"))
    mysql_user = getCommProperties("mysql.user")
    mysql_password = getCommProperties("mysql.password")

    try:
        # connect
        conn = mdb.connect(host=mysql_ip, port=mysql_port, user=mysql_user, passwd=mysql_password)
        # conn = mdb.connect(host=mysql_ip, port=mysql_port, user=mysql_user, passwd=mysql_password, database=mysql_database, charset='utf8')
        conn.close()
        print("check finished sucessfully.")        
        log.info("check mgr db user/password correct!")
    except:
        import traceback
        print("======mgr mysql user/password error!======")
        log.info("mgr mysql user/password error {}".format(traceback.format_exc()))
        traceback.print_exc()
        sys.exit(0)


def checkSignDbAuthorized():
    print ("check sign database user/password...")
    # get properties
    mysql_ip = getCommProperties("sign.mysql.ip")
    mysql_port = int(getCommProperties("sign.mysql.port"))
    mysql_user = getCommProperties("sign.mysql.user")
    mysql_password = getCommProperties("sign.mysql.password")

    try:
        # connect
        conn = mdb.connect(host=mysql_ip, port=mysql_port, user=mysql_user, passwd=mysql_password)
        conn.close()
        print("check finished sucessfully.")        
        log.info("check sign db user/password correct!")
    except:
        import traceback
        print("======sign mysql user/password error!======")
        log.info("sign mysql user/password error {}".format(traceback.format_exc()))
        traceback.print_exc()
        sys.exit(0)

# init table and table's default data of nodemgr
def initNodeMgrTable(script_dir,init_both=True):
    print ("init mgr database tables...")
    # get properties
    mysql_ip = getCommProperties("mysql.ip")
    mysql_port = int(getCommProperties("mysql.port"))
    mysql_user = getCommProperties("mysql.user")
    mysql_password = getCommProperties("mysql.password")
    mysql_database = getCommProperties("mysql.database")
    
      # 0:ecdsa, 1:gm 
    encrypt_type = int(getCommProperties("encrypt.type"))
    
    # read .sql content
    create_sql_path = script_dir + "/webase-ddl.sql"
    if encrypt_type == 1:
        init_sql_path = script_dir + "/gm/webase-dml-gm.sql"
    else:
        init_sql_path = script_dir + "/webase-dml.sql"
    # create table
    create_sql_list=readSqlContent(create_sql_path)
    # init table data
    init_sql_list=readSqlContent(init_sql_path)

    try:
        # connect
        conn = mdb.connect(host=mysql_ip, port=mysql_port, user=mysql_user, passwd=mysql_password, database=mysql_database, charset='utf8')
        conn.autocommit(1)
        cursor = conn.cursor()

        log.info("start create tables...")
        for sql_item in create_sql_list:
            log.info(sql_item)
            cursor.execute(sql_item)

        # if both create table and init table data
        if init_both:
            log.info("start init default data of tables...")
            for sql_item in init_sql_list:
                log.info(sql_item)
                cursor.execute(sql_item)
        
        print ("==============     script  init  success!     ==============")
        log.info("init mgr tables success!")
        cursor.close()
        conn.close()
    except:
        import traceback
        print ("============== script init  fail. Please view log file (default path:./log/). ==============")
        log.info("init mgr database tables error {}".format(traceback.format_exc()))
        traceback.print_exc()
        sys.exit(0)

def readSqlContent(sql_path):
    log.info("reading node manager table sql file {}".format(sql_path))        
    # read .sql file in webase-node-mgr/script(/gm)
    with open(sql_path,encoding="utf-8",mode="r") as f:  
        data = f.read()
        lines = data.splitlines()
        sql_data = ''
	    # remove -- comment
        for line in lines:
            if len(line) == 0:
                continue
            elif line.startswith("--"):
                continue
            else:
                sql_data += line
        sql_list = sql_data.split(';')[:-1]
        sql_list = [x.replace('\n', ' ') if '\n' in x else x for x in sql_list]
        return sql_list

if __name__ == '__main__':
    pass
