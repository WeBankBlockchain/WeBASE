#!/bin/bash

####### error code
SUCCESS=0

PARAM_ERROR=5

## default one host, one node+front
old_version="v1.4.3"
new_version="v1.5.0"

# download url prefix
cdn_url_pre="https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/"
## zip name, todo webase-web-h5
zip_list=["webase-front","webase-node-mgr","webase-sign","webase-web"]
#zip_list="webase-front.zip webase-node-mgr.zip webase-sign.zip webase-web.zip"

## re-download zip
force_download_zip="true"

####### 参数解析 #######
cmdname=$(basename "$0")

# usage help doc.
usage() {
    cat << USAGE  >&2
Usage:
    $cmdname [-C node_count]

    -o    old version, ex: v1.4.3
    -n    new version, ex: v1.5.0
    -f    force download new zip and rm old zip in ${PWD}
USAGE
    exit ${PARAM_ERROR}
}


while getopts C:h OPT;do
    case ${OPT} in
        C)
            node_count="$OPTARG"
            ;;
        h)
            usage
            exit ${PARAM_ERROR}
            ;;
        \?)
            usage
            exit ${PARAM_ERROR}
            ;;
    esac
done

#!/usr/bin/env bash

### 需要文档指明脚本做了什么操作，生产环境的运维如果分步操作怎么完成

# 输入旧的版本，如v1.4.3，新的版本号，v1.5.0

## download zip
function download_zip() {
    for webase_name in $zip_list
    do
        pull_zip "$webase_name"
        copy "$webase_name"
    done
}


function pull_zip() {
    local webase_name="$1"
    local zip="${webase_name}.zip"
    if [[ "${force_download_zip}" == "true" ]];then
        echo "now force re-download zip of webase"
        # delete old zip
        if [[ -f "$zip" ]];then
            rm -f "$zip"
        fi
    fi
    echo "pull zip of $zip"
    wget "${cdn_url_pre}/${new_version}/${zip}" 
    # webase-web.zip => webase-web-v1.5.0
    local temp_package_name="${webase_name}-${new_version}"
    unzip_package "$zip" "$temp_package_name"
}

## unzip
function unzip_package() {
    local zip="$1"
    local target_dir="$2"
    echo "unzip zip of $webase_name to unzip ${target_dir}"
    unzip -o "${zip}" -d "${PWD}/$target_dir"
}

## copy config and cert to new unzip dir
# first copy from old webase, then backup and rename old webase
function copy_webase() {
    local webase_name="$1"
    case ${webase_name} in
        webase-web)
            copy_web
            ;;
        webase-front)
            copy_front
            ;;
        webase-node-mgr)
            copy_node_mgr
            ;;        
        webase-sign)
            copy_sign
            ;;            
        \?)
            usage
            exit ${PARAM_ERROR}
            ;;
    esac


    echo "copy $webase_name config"
    if [[ "${webase_name}x" == "webase-webx" ]]; then

    fi
    echo "copy config files for $zip from"
    # webase-web.zip => webase-web-
    echo "change name from $zip to $temp_package_name "
    unzip -o "${zip}" -d "${PWD}/$temp_package_name"

}

# copy webase-web and webase-web-h5
function copy_web() {
    # no need copy from old web, just use the new one
}

function copy_front() {
    copy "${PWD}/webase-front/conf/*.yml" "${PWD}/webase-front-${new_version}/conf/" 
    copy "${PWD}/webase-front/conf/*.crt" "${PWD}/webase-front-${new_version}/conf/" 
    copy "${PWD}/webase-front/conf/*.key" "${PWD}/webase-front-${new_version}/conf/" 
    copy "${PWD}/webase-front/conf/*.so" "${PWD}/webase-front-${new_version}/conf/" 
    backup "webase-front"
}

function copy_node_mgr() {
    copy "${PWD}/webase-node-mgr/conf/*.yml" "${PWD}/webase-node-mgr-${new_version}/conf/" 
    copy -r "${PWD}/webase-node-mgr/conf/log" "${PWD}/webase-node-mgr-${new_version}/conf/" 
    backup "webase-node-mgr"
    update_node_mgr_yml
}

function copy_sign() {
    copy "${PWD}/webase-sign/conf/*.yml" "${PWD}/webase-sign-${new_version}/conf/" 
    backup "webase-sign"
}

function stop_all() {
    echo "now stop webase all"
    python3 deploy.py stopAll  || (echo "stopAll failed!" && exit)
}

function start_all() {
    echo "now start webase all"
    python3 deploy.py startAll || (echo "startAll failed!" && exit)
}

# backup webase dir
function backup() {
    local webase_name="$1"
    # stop all
    echo "now backup old data"
    mv "${webase_name}" "${webase_name}-${old_version}" || (echo "backup ${webase_name} failed!" && exit)
    mv "${webase_name}-${new-version}" "${webase_name}" || (echo "backup ${webase_name} failed!" && exit)
}


# upgrade table of node-mgr 
function upgrade_mgr_sql() {
    # check whether old=>new .sql shell in new webase-node-mgr/script
    mgr_script_name="${PWD}/webase-node-mgr/script/v${old_version}_v${new_version}.sql"
    if [[ -f ${mgr_script_name} ]];then
        # get sql config of mgr from common.properties
        local ip=${prop "mysql.ip"}
        local port=${prop "mysql.port"}
        local user=${prop "mysql.user"}
        local password=${prop "mysql.password"}
        local database=${prop "mysql.database"}
        local backup_mgr_dir="${PWD}/webase-node-mgr-${old_version}/backup_node_mgr_${old_version}.sql"
        echo "now backup the whole database of node-mgr in $backup_mgr_dir"
        mysqldump  --user=$user --password=$password $database > $backup_mgr_dir
        # exec .sql by mysql -e
        echo "now upgrade database of node-mgr with script $mgr_script_name"
        mysql --user=$user --password=$password --host=$ip --port=$port --database=$database -e${mgr_script_name} $--default-character-set=utf8; 
    else
        echo "node-mgr upgrade sql file of ${mgr_script_name} not exist!"
    fi
}

# upgrade table of sign
function upgrade_sign_sql() {
    # check whether old=>new .sql shell in new webase-sign/script
    sign_script_name="${PWD}/webase-sign/script/v${old_version}_v${new_version}.sql"
    if [[ -f ${sign_script_name} ]];then
        # get sql config of sign from common.properties
        local ip=${prop "sign.mysql.ip"}
        local port=${prop "sign.mysql.port"}
        local user=${prop "sign.mysql.user"}
        local password=${prop "sign.mysql.password"}
        local database=${prop "sign.mysql.database"}
        # exec .sql by mysql -e
        mysql --user=$user --password=$password --host=$ip --port=$port --database=$database -e${sign_script_name} $--default-character-set=utf8; 
    else
        echo "sign upgrade sql file of ${sign_script_name} not exist!"
    fi
}


config_properties="${PWD}/common.properties"
# 定义一个函数从properties文件读取key
function prop() {
	[ -f "$config_properties" ] && grep -P "^\s*[^#]?${1}=.*$" $config_properties | cut -d'=' -f2
}


## 版本号获取数字，v1.5.0 => 150
function get_version_num() {
    old_version_num=`echo "${old_version}" | tr -cd "[0-9]"`
    new_version_num=`echo "${new_version}" | tr -cd "[0-9]"`
}

# update old yml
function update_node_mgr_yml() {
    mgr_yml="${PWD}/webase-node-mgr/conf/application.yml"    
    # v1.5.0 key config to check if already add
    if [ `grep -c "appStatusCheckCycle" ${mgr_yml}` -eq '0' ]; then
        # 将constant:开头替换为
        local old_app_config="constant:"
        local new_app_config="constant:\n  deployedModifyEnable: true\n  appRequestTimeOut: 300000\n  appStatusCheckCycle: 3000\n"
        sed_file ${old_app_config} ${new_app_config} ${mgr_yml}        
    fi
    if [ `grep -c "\/api\/*" ${mgr_yml}` -eq '0' ]; then
        # 需要空格开头
        local old_url_config="permitUrlArray: \/account\/login"
        local new_url_config="\ \ permitUrlArray: \/account\/login,\/account\/pictureCheckCode,\/login,\/user\/privateKey\/**,\/encrypt,\/version,\/front\/refresh,\/api\/*"
        sed_file ${old_url_config} ${new_url_config} ${mgr_yml}
    fi
}

function sed_file() {
    local old_config="$1"
    local new_config="$2"
    local file_path="$3"
    sed -i "/${old_config}/c${new_config}" ${file_path}
}

# 从common.properties中获取两个数据库密码

# 下载新的zip包，已存在则删除

# 解压新的zip包到webase-front.zip => webase-front-v1.5.0

# 停止原有的，python3 deploy.py stopAll

# webase-web 直接复制全部
# 复制已有front的conf/*.yml, *.key, *.crt, *.so，覆盖当前的文件
# 复制已有sign的conf/*.yml
# 复制已有node-mgr已有的conf的*.yml，conf/log目录
## 更新旧的yml

# mv操作，备份已有的，如
# webase-web => webase-web-v143
# webase-web-150 => webase-web

# 备份node-mgr数据库
# 到node-mgr中检测script/upgrade目录，有匹配v143开头的，v150的结尾的，有则执行 mysql  -e "source $sql_file"
# 到sign...同上（当前版本不增加）

# 启动新的，执行python3 deploy.py startAll


