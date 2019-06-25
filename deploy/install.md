# 一键部署说明

[TOC]

​	一键部署可以快速搭建WeBASE环境。包括节点（fisco-bcos）、节点前置（WeBASE-Front）、节点管理（WeBASE-Node-Manager）、管理平台（WeBASE-Web）。

​	部署脚本会拉取相关安装包进行部署（需保持网络畅通），重复部署可根据提示进行相关操作。

## 1、前提条件

| 环境   | 版本                   |
| ------ | ---------------------- |
| Java   | jdk1.8.0_121或以上版本 |
| python | 2.7                 |
| MySQL-python | 1.2.5 |
| mysql | mysql-5.6或以上版本 |

**备注：** 安装说明请参看 [附录7](#7附录)

## 2、拉取部署脚本

获取部署安装包：
```shell
wget https://github.com/mingzhenliu/sss/releases/download/111/webase-deploy.zip
```
解压安装包：
```shell
unzip webase-deploy.zip
```
进入目录：
```shell
cd webase-deploy
```

## 3、修改配置

① 可以使用以下命令修改，也可以直接修改文件（vi common.properties），没有变化的可以不修改

② 数据库需要提前安装（数据库安装请参看 [附录7.4](#74-数据库部署)）

③ 服务端口不能小于1024

```shell
数据库ip：sed -i "s%127.0.0.1%${your_db_ip}%g" common.properties
数据库端口：sed -i "s%3306%${your_db_port}%g" common.properties
数据库用户名：sed -i "s%dbUsername%${your_db_account}%g" common.properties
数据库密码：sed -i "s%dbPassword%${your_db_password}%g" common.properties
数据库名称：sed -i "s%db_mgr%${your_db_name}%g" common.properties

web服务端口：sed -i "s%8080%${your_web_port}%g" common.properties
mgr服务端口：sed -i "s%8081%${your_mgr_port}%g" common.properties
front服务端口：sed -i "s%8082%${your_front_port}%g" common.properties

节点fisco版本：sed -i "s%2.0.0-rc2%${your_fisco_version}%g" common.properties
节点安装个数：sed -i "s%nodeCounts%${your_node_counts}%g" common.properties
节点p2p端口：sed -i "s%30300%${your_p2p_port}%g" common.properties
节点channel端口：sed -i "s%20200%${your_channel_port}%g" common.properties
节点rpc端口：sed -i "s%8545%${your_rpc_port}%g" common.properties
前置h2数据库名：sed -i "s%/db_front%${your_dist_dir}%g" common.properties
前置要监控的磁盘路径：sed -i "s%/data%${your_dist_dir}%g" common.properties

例子（将磁盘路径由/data改为/home）：sed -i "s%/data%/home%g" common.properties
```

## 4、部署
部署所有服务：
```shell
python deploy.py startAll
```
停止所有服务：
```shell
python deploy.py stopAll
```
单独启停命令和说明可查看帮助：
```shell
python deploy.py help
```

**备注：** 部署过程出现问题可以查看 [常见问题8](#8常见问题)

## 5、访问

管理平台：

```
http://{deployIP}:{webPort}
```

节点前置控制台：

```
http://{deployIP}:{frontPort}/webase-front
```

**备注：**部署服务器IP和相关服务端口需对应修改

## 6、日志路径

```
部署日志：log/
节点日志：nodes/127.0.0.1/node*/log/
web服务日志：webase-web/log/
mgr服务日志：webase-node-mgr/logs/
front服务日志：webase-front/log/
```

## 7、附录

### 7.1 Java环境部署

此处给出简单步骤，供快速查阅。更详细的步骤，请参考[官网](http://www.oracle.com/technetwork/java/javase/downloads/index.html)。

（1）从[官网](http://www.oracle.com/technetwork/java/javase/downloads/index.html)下载对应版本的java安装包，并解压到相应目录

```shell
mkdir /software
tar -zxvf jdkXXX.tar.gz /software/
```

（2）配置环境变量

```shell
export JAVA_HOME=/software/jdk1.8.0_121
export PATH=$JAVA_HOME/bin:$PATH 
export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
```

### 7.2 Python部署

```shell
pip install requests 或 sudo yum install -y requests
```

### 7.3 MySQL-python部署

- CentOS

  ```
  sudo yum install -y MySQL-python
  ```

- Ubuntu

  ```
  sudo apt-get install -y python-pip
  sudo pip install MySQL-python
  ```

### 7.4 数据库部署

此处以Centos/Fedora为例。

（1）切换到root

```shell
sudo -s
```

（2）安装mysql

```shell
yum install mysql*
#某些版本的linux，需要安装mariadb，mariadb是mysql的一个分支
yum install mariadb*
```

（3）启动mysql

```shell
service mysqld start
#若安装了mariadb，则使用下面的命令启动
systemctl start mariadb.service
```

（4）初始化数据库用户

初次登录

```shell
mysql -u root
```

给root设置密码和授权远程访问

```sql
mysql > SET PASSWORD FOR 'root'@'localhost' = PASSWORD('123456');
mysql > GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '123456' WITH GRANT OPTION;
```

**安全温馨提示：**

1. 例子中给出的数据库密码（123456）仅为样例，强烈建议设置成复杂密码
2. 例子中的远程授权设置会使数据库在所有网络上都可以访问，请按具体的网络拓扑和权限控制情况，设置网络和权限帐号

授权test用户本地访问数据库

```sql
mysql > create user 'test'@'localhost' identified by '123456';
```

（5）测试连接

另开一个ssh测试本地用户test是否可以登录数据库

```shell
mysql -utest -p123456 -h 127.0.0.1 -P 3306
```

登陆成功后，执行以下sql语句，若出现错误，则用户授权不成功

```sql
mysql > show databases;
mysql > use test;
```

（6）创建数据库

登录数据库

```shell
mysql -utest -p123456 -h 127.0.0.1 -P 3306
```

创建数据库

```sql
mysql > create database db_browser;
```

## 8、常见问题

### 8.1 数据库安装后登录报错

腾讯云centos mysql安装完成后，登录报错：Access denied for user 'root'@'localhost'

① 编辑 /etc/my.cnf ，在[mysqld] 部分最后添加一行

```
skip-grant-tables
```

② 保存后重启mysql

```shell
service mysqld restart
```

③ 输入以下命令，回车后输入密码再回车登录mysql

```
mysql -uroot -p mysql
```

### 8.2 找不到MySQLdb

```
Traceback (most recent call last):
...
ImportError: No module named MySQLdb
```

答：MySQL-python安装请参看部署附录7.3

### 8.3 部署时编译包下载慢

```
...
Connecting to github-production-release-asset-2e65be.s3.amazonaws.com (github-production-release-asset-2e65be.s3.amazonaws.com)|52.216.112.19|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 22793550 (22M) [application/octet-stream]
Saving to: ‘webase-front.zip’

 0% [                                                                                                                                ] 77,974      37.8KB/s    
```

答：部署过程会下载工程编译包，可能会因为网络原因导致过慢。此时，可以先手动下载（ [webase-web](https://github.com/WeBankFinTech/WeBASELargeFiles/releases/download/WeBASEV1.0.0/webase-web.zip) 、[webase-node-mgr](https://github.com/WeBankFinTech/WeBASELargeFiles/releases/download/WeBASEV1.0.0/webase-node-mgr.zip) 、[webase-front](https://github.com/WeBankFinTech/WeBASELargeFiles/releases/download/WeBASEV1.0.0/webase-front.zip)），再上传至服务器webase-deploy目录，在部署过程中根据提示不再重新下载编译包。

### 8.4 部署时数据库访问报错

```
...
checking database connection
Traceback (most recent call last):
  File "/data/temp/webase-deploy/comm/mysql.py", line 21, in dbConnect
    conn = mdb.connect(host=mysql_ip, port=mysql_port, user=mysql_user, passwd=mysql_password, charset='utf8')
  File "/usr/lib64/python2.7/site-packages/MySQLdb/__init__.py", line 81, in Connect
    return Connection(*args, **kwargs)
  File "/usr/lib64/python2.7/site-packages/MySQLdb/connections.py", line 193, in __init__
    super(Connection, self).__init__(*args, **kwargs2)
OperationalError: (1045, "Access denied for user 'root'@'localhost' (using password: YES)")
```

答：确认数据库用户名和密码
