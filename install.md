# 目录
> * [依赖环境](#chapter-1)
> * [节点管理安装](#chapter-2)
> * [节点前置服务安装](#chapter-3)
> * [web管理平台安装](#chapter-4)


本安装文档仅描述了在一台服务器上安装搭建WeBASE的过程，目的是为了让开发者对WeBASE的部署搭建、运行、测试等有个整体的认识。如要用于生产环境，部署安装的流程和原理是一样的，但需要更多考虑分布式系统下服务的部署，需要有容错、容灾等的能力。

# 1. <a id="chapter-1"></a>依赖环境
软件 | 软件要求
------|--------
gradle      |	gradle4.9或更高版本（构建工具）
java        |   1.8.0_181或更高版本
mysql版本   |   5.5及以上版本（框架运行依赖）
python | Python2.7 

运行服务器要求：1台普通安装linux系统的机器即可。

# 2. <a id="chapter-2"></a>节点管理安装
## 2.1. 获取源代码
```
git clone https://github.com/WeBankFinTech/webase-node-mgr.git
```

## 2.2 编译代码
在代码的根目录webase-node-mgr执行构建命令：
```
gradle build
```
构建完成后，会在/usr/local/app/webase-node-mgr目录生成已编译的代码。

## 2.3 创建数据库
### 2.3.1 修改脚本配置
进入数据库脚本目录
```
cd  /usr/local/app/webase-node-mgr/conf/script
```
修改数据库连接信息：
```
修改数据库名称：sed -i "s/fisco-bcos-data/${your_db_name}/g" fisco-bcos.sh
修改数据库用户名：sed -i "s/defaultAccount/${your_db_account}/g" fisco-bcos.sh
修改数据库密码：sed -i "s/defaultPassword/${your_db_password}/g" fisco-bcos.sh
```
例如：将数据库用户名修改为root，则执行：
```
sed -i "s/defaultAccount/root/g" fisco-bcos.sh
```

### 2.3.2 运行数据库脚本
执行命令：sh  fisco-bcos.sh  ${dbIP}  ${dbPort}
如：
```
sh  fisco-bcos.sh  123.207.235.12 3306
```

## 2.4 节点服务的配置及启动
### 2.4.1 服务配置修改
进入到已编译的代码根目录：
```
cd /usr/local/app/webase-node-mgr/conf
```
修改服务配置：
```
修改当前服务端口：sed -i "s/8080/${your_server_port}/g" application.yml
修改数据库IP：sed -i "s/127.0.0.1/${your_db_port}/g" application.yml
修改数据库名称：sed -i "s/fisco-bcos-data/${your_db_name}/g" application.yml
修改数据库用户名：sed -i "s/defaultAccount/${your_db_account}/g" application.yml
修改数据库密码：sed -i "s/defaultPassword/${your_db_password}/g" application.yml
```

### 2.4.2 服务启停
进入到已编译的代码根目录：
```
cd /usr/local/app/webase-node-mgr
```
启动：
```
sh start.sh
```
停止：
```
sh stop.sh
```
状态检查：
```
sh serverStatus.sh
```
### 2.4.3 查看日志
全量日志：
```
/usr/local/app/logs/webase-node-mgr/node-mgr.log
```
错误日志：
```
/usr/local/app/logs/webase-node-mgr/node-mgr-error.log
```

## 2.5 初始化基础合约
### 2.5.1 前提条件
节点正常运行
节点管理服务正常运行
节点前置正常运行

### 2.5.2 修改脚本配置
进入合约脚本目录：
```
cd /usr/local/app/webase-node-mgr/conf/contract
```
修改配置中的前置服务信息：
```
修改前置服务IP：sed -i "s/defaultFrontIp /${your_front_ip}/g"  contract-init.sh
修改前置服务的端口：sed -i "s/defaultFrontPort /${your_front_port}/g"  contract-init.sh
```
### 2.5.3 运行脚本
执行命令：
```
sh contract-init.sh
```
如果脚本中三个合约部署返回结果的code都是0,则表示合约所有合约都部署成功


# 3. <a id="chapter-3"></a>节点前置服务安装

## 3.1 拉取代码

执行命令：
```
git clone http://xxx/webase-front.git
```

## 3.2 编译代码

在代码的根目录webase-front执行构建命令：
```
gradle build
```
构建完成后，会在根目录webase-front下生成已编译的代码目录dist。

## 3.3 修改配置
进入目录：
```
cd dist/conf
```
```
修改当前服务端口：sed -i "s/8081/${your_server_port}/g" application.yml
修改机构名称：sed -i "s/orgTest/${your_org_name}/g" application.yml
修改节点目录：sed -i "s/\/data\/app\/build\/node0/${your_node_dir}/g" application.yml
修改节点管理服务ip端口：sed -i "s/127.0.0.1:8082/${your_ip_port}/g" application.yml
例子（将端口由8081改为8090）：sed -i "s/8081/8090/g" application.yml
```
进入目录：
```
cd dist/report
```
```
修改节点管理服务ip：sed -i "s/127.0.0.1/${your_ip }/g" config.json
修改节点管理服务端口：sed -i "s/8082/${your_ port}/g" config.json
修改节点目录：sed -i "s/\/data\/app\/build\/node0/${your_node_dir}/g" config.json
```

## 3.4 服务启停

进入到已编译的代码根目录：
```shell
cd dist
```
```shell
启动：sh start.sh
停止：sh stop.sh
检查：sh status.sh
```

## 3.5 查看日志

进入到已编译的代码根目录：
```
cd dist
```
```
前置服务日志：tail -f log/webase-front.log
web3连接日志：tail -f log/web3sdk.log
report服务日志：tail -f dist/report/log/report.log
```

# 4. <a id="chapter-4"></a>web管理平台安装
## 4.1	安装nginx
### 4.1.1安装依赖
```
yum -y install gcc pcre-devel zlib-devel openssl openssl-devel
```
### 4.1.2获取nginx
```
cd /usr/local
wge t http://nginx.org/download/nginx-1.10.2.tar.gz  (版本号可换)
```
### 4.1.3安装nginx
```
tar -zxvf nginx-1.10.2.tar.gz
cd nginx-1.10.2
./configure --prefix=/usr/local/nginx
make
make install
```

## 4.2 获取源代码
```
cd /usr/local/app
git clone https://github.com/WeBankFinTech/webase-web.git
```
## 4.3 修改配置
在代码库中docs文件下有nginx配置文件，直接可以拿来替换安装的nginx的配置文件nginx.conf；
然后修改nginx.conf；

进入nginx配置文件（这里nginx安装在/usr/local下面，如果这里没找到，可以到/etc下寻找）
```
    cd /usr/local/nginx/conf
```

### 4.3.1 修改web服务端口
```
    sed -i "s/3002/${your_server_port}/g" nginx.conf
```
例如：
```
    sed -i "s/3002/8080/g" nginx.conf   你修改的服务端口是8080
```

### 4.3.2 修改服务ip
```
`sed -i "s/ 10.0.0.1 /${your_server_ip}/g" nginx.conf
```
例如： 
```
    sed -i "s/ 10.0.0.1 /192.168.0.1/g" nginx.conf
```
你修改的服务ip是192.168.0.1,也可以修改成域名
### 4.3.3 修改静态文件路径
```
    sed -i "s/\ /data\/webase-web \/dist /${your_file_route}/g" nginx.conf
```

### 4.3.4 修改mgr服务ip和端口
```
sed -i "s/ 10.0.0.1:8083 /${your_mgrServer_ipPort}/g" nginx.conf
````

服务器已有nginx可按照以下修改，

```Nginx
upstream node_mgr_server{
<<<<<<< HEAD
        server 10.0.0.1:8083; //步骤三 节点管理服务地址及端口
=======
        server 10.107.119.91:8082;   //配置mgr地址及端口
}
server {
    listen      8088 default_server;  #配置服务端口，需要开通网络策略
     server_name   10.107.105.18;    #配置服务地址，可以配置为域名
     location / {    
root    /data/fisco-bcos-web/dist;   #静态文件路径，请指向下载代码的dist目录
        index  index.html index.htm;
        try_files $uri $uri/ /index.html =404;
     }
  	# Load configuration files for the default server block.
    include /etc/nginx/default.d/*.conf;
location /api {
proxy_pass    http:// node_mgr_server /;    
       proxy_set_header         Host                          $host;
       proxy_set_header         X-Real-IP                 $remote_addr;
       proxy_set_header        X-Forwarded-For     $proxy_add_x_forwarded_for;
    }
    error_page 404 /404.html;
            location = /40x.html {
>>>>>>> 942022a2ff7238e045d85e173eba0d5a2513dd73
    }
    server {
        listen       3002 default_server;   //步骤一 前端端口
        server_name  10.0.0.1;         //步骤一 前端地址，可配置为域名
        location / {
                root    /data/webase-web/dist;   //步骤二 前端文件路径
                index  index.html index.htm;
                try_files $uri $uri/ /index.html =404;
                }

        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;

        location /mgr {
                    proxy_pass    http://node_mgr_server/;    		
                    proxy_set_header		Host				$host;
                        proxy_set_header		X-Real-IP			$remote_addr;
                        proxy_set_header		X-Forwarded-For		$proxy_add_x_forwarded_for;
                }
        }
```

## 4.4 启动服务
找到nginx服务目录
可以使用命令：
whereis nginx
进入目录并启动：
cd /usr/local/nginx
启动命令：
```
/usr/local/nginx/sbin/nginx
```
停止命令：
```
/usr/local/nginx/sbin/nginx –s stop
```

## 4.5 打开浏览器
输入url：上面的ip或域名+端口
出现页面后输入初始帐号密码：admin/Abcd1234

