#!/bin/bash

set -e


### 需要文档指明脚本做了什么操作，生产环境的运维如果分步操作怎么完成
################################################
# 下载新的zip包，已存在则重命名

# 解压新的zip包到webase-front.zip => webase-front-v1.5.0

# 停止原有的，python3 deploy.py stopAll

# webase-web 直接复制全部
# 复制已有front的conf/*.yml, *.key, *.crt, *.so，覆盖当前的文件
# 复制已有sign的conf/*.yml
# 复制已有node-mgr已有的conf的*.yml，conf/log目录
# 更新旧的yml，更新版本号

# mv操作，备份已有的，如
# webase-web => webase-web-v143
# webase-web-150 => webase-web

# 备份node-mgr数据库到webase-node-mgr-v1.5.0/backup.sql
# 从common.properties中获取两个数据库密码

# 到node-mgr中检测script/upgrade目录，有匹配v143开头的，v150的结尾的，有则执行 mysql  -e "source $sql_file"
# 到sign...同上（当前版本不增加）

# 启动新的，执行python3 deploy.py startAll
################################################

####### error code
SUCCESS=0

PARAM_ERROR=5

## default one host, one node+front
old_version="v1.4.3"
new_version="v1.5.0"
## zip name, todo webase-web-h5
zip_list=("webase-sign" "webase-front" "webase-node-mgr" "webase-web" "webase-web-h5")

# download url prefix
cdn_url_pre="https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/"
logfile=${PWD}/upgrade.log

## re-download zip
force_download_zip="false"

LOG_WARN()
{
    local content=${1}
    echo -e "\033[31m[WARN] ${content}\033[0m"
}

LOG_INFO()
{
    local content=${1}
    echo -e "\033[32m[INFO] ${content}\033[0m"
}

####### 参数解析 #######
cmdname=$(basename "$0")

# usage help doc.
usage() {
    cat << USAGE  >&2
Usage:
    $cmdname [-o old_version] [-n new_version]

    -o    old version, ex: v1.4.3
    -n    new version, ex: v1.5.0
USAGE
    exit ${PARAM_ERROR}
}


while getopts o:n:h OPT;do
    case ${OPT} in
        o)
            old_version="$OPTARG"
            ;;
        n)
            new_version="$OPTARG"
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


function main() {
    LOG_INFO "start pull zip of new webase..."
    # pull
    for webase_name in ${zip_list[@]};
    do
        pull_zip "$webase_name" || (LOG_WARN "pull_zip $webase_name failed!" && exit 1)
    done
    # stop
    LOG_INFO "==========now webase stop all=========="
    python3 deploy.py stopAll  || (LOG_WARN "==========stopAll failed!==========" && exit 1)
    # change new webase's config file, backup old webase and data
    for webase_name in ${zip_list[@]};
    do
        copy_webase "$webase_name" || (LOG_WARN "copy_webase $webase_name failed!" && exit 1)
    done
    # update version
    LOG_INFO "==========now update webase version in yml=========="
    update_webase_yml_version
    # restart
    LOG_INFO "==========now webase start all=========="
    python3 deploy.py startAll  || (LOG_WARN "==========startAll failed!==========" && exit 1)
}


function pull_zip() {
    local webase_name="$1"
    local zip="${webase_name}.zip"
    # if [[ "${force_download_zip}" == "true" ]];then
    echo "now rename old zip of webase"
    # delete old zip
    if [[ -f "$zip" ]];then
        mv "$zip" "${webase_name}-${old_version}.zip"
    fi
    # fi
    LOG_INFO "pull zip of $zip"
    curl -#LO "${cdn_url_pre}${new_version}/${zip}" 
    # webase-web.zip => webase-web-v1.5.0/webase-web
    #注：unzip后变成了webase-web-v1.5.0/webase-web
    unzip -o "$zip" -d "${webase_name}-${new_version}"
}

## copy config and cert to new unzip dir
# first copy from old webase, then backup and rename old webase
function copy_webase() {
    local webase_name="$1"
    case ${webase_name} in
        "webase-web")
            backup "webase-web-h5"
            backup "webase-web"
            ;;
        "webase-front")
            copy_front
            backup "webase-front"    
            ;;
        "webase-node-mgr")
            copy_node_mgr
            backup "webase-node-mgr"
            update_node_mgr_yml
            upgrade_mgr_sql
            ;;        
        "webase-sign")
            copy_sign
            backup "webase-sign"
            ;;            
        \?)
            usage
            exit ${PARAM_ERROR}
            ;;
    esac

}

# copy webase-web and webase-web-h5
# no need copy from old web, just use the new one
# function copy_web() 

function copy_front() {     
    LOG_INFO "copy webase-front config files"
    if [[ -d "${PWD}/webase-front" ]]; then
        cp "${PWD}/webase-front/conf/application.yml" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp "${PWD}/webase-front/conf/log4j2.xml" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp "${PWD}/webase-front/conf/ca.crt" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp "${PWD}/webase-front/conf/sdk.crt" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp "${PWD}/webase-front/conf/sdk.key" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp -r "${PWD}/webase-front/conf/gm" "${PWD}/webase-front-${new_version}/webase-front/conf/"         
        cp "${PWD}/webase-front/conf/libsigar-aarch64-linux.so" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp "${PWD}/webase-front/conf/libsigar-amd64-linux.so" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp "${PWD}/webase-front/conf/libsigar-universal64-macosx.dylib" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp "${PWD}/webase-front/conf/libsigar-x86-linux.so" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        if [[ -f "${PWD}/webase-front/conf/node.key" ]]; then
            cp "${PWD}/webase-front/conf/node.crt" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
            cp "${PWD}/webase-front/conf/node.key" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        fi
    else
        LOG_WARN "copy directory of ${PWD}/webase-front not exist!"
    fi
}

function copy_node_mgr() {
    LOG_INFO "copy webase-node-mgr config files"
    if [[ -d "${PWD}/webase-node-mgr" ]]; then    
        cp "${PWD}/webase-node-mgr/conf/application.yml" "${PWD}/webase-node-mgr-${new_version}/webase-node-mgr/conf/" 
        #cp -r "${PWD}/webase-node-mgr/conf/log" "${PWD}/webase-node-mgr-${new_version}/webase-node-mgr/conf/" 
    else
        LOG_WARN "copy directory of webase-node-mgr not exist!"
    fi
}

function copy_sign() {
    LOG_INFO "copy sign config files"
    if [[ -d "${PWD}/webase-sign" ]]; then       
        cp "${PWD}/webase-sign/conf/application.yml" "${PWD}/webase-sign-${new_version}/webase-sign/conf/" 
    else
        LOG_WARN "config directory of webase-sign not exist!"
    fi
}

# backup webase dir
function backup() {
    local webase_name="$1"
    # stop all
    LOG_INFO "now backup old data of ${webase_name}"
    if [[ -d "${PWD}/${webase_name}" ]]; then
        mv "${PWD}/${webase_name}" "${PWD}/${webase_name}-${old_version}" || (LOG_WARN "backup ${PWD}/${webase_name} failed!" && exit)
    else
        LOG_WARN "backup directory of ${PWD}/${webase_name} not exist!"
    fi    
    mv "${PWD}/${webase_name}-${new_version}/${webase_name}" "${PWD}/${webase_name}" || (LOG_WARN "backup ${PWD}/${webase_name}-${new_version}/${webase_name} failed!" && exit)
}


config_properties="${PWD}/common.properties"
# 定义一个函数从properties文件读取key
function prop() {
    local key="${1}"
	if [[ -f "$config_properties" ]]; then
        dos2unix $config_properties
        grep -P "^\s*[^#]?${key}=.*$" $config_properties | cut -d'=' -f2
    fi
}

## 版本号获取数字，v1.5.0 => 150
function get_version_num() {
    old_version_num=`echo "${old_version}" | tr -cd "[0-9]"`
    new_version_num=`echo "${new_version}" | tr -cd "[0-9]"`
}

# upgrade table of node-mgr after backup webase-node-mgr dir
function upgrade_mgr_sql() {
    # check whether old=>new .sql shell in new webase-node-mgr/script
    mgr_script_name="${PWD}/webase-node-mgr/script/v${old_version_num}_v${old_version_num}.sql"
    if [[ -f "${mgr_script_name}" ]];then
        # get sql config of mgr from common.properties
        local ip=$(prop "mysql.ip")
        local port=$(prop "mysql.port")
        local user=$(prop "mysql.user")
        local password=$(prop "mysql.password")
        local database=$(prop "mysql.database")
        LOG_INFO "get propertise user: ${user} host: ${ip} port: ${port} db: ${database} "
        local backup_mgr_dir="webase-node-mgr-${old_version}/backup_node_mgr_${old_version}.sql"
        LOG_INFO "now backup the whole database of node-mgr in $backup_mgr_dir"
        mysqldump  --user=${user} --password=${password} --host=${ip} --port=${port} ${database} > ${backup_mgr_dir}
        # exec .sql by mysql -e
        LOG_INFO "now upgrade database of node-mgr with script $mgr_script_name"
        mysql --user=$user --password=$password --host=$ip --port=$port --database=$database --default-character-set=utf8 -e "source ${mgr_script_name}"
    else
        LOG_WARN "node-mgr upgrade sql file of ${mgr_script_name} not exist!"
    fi
}

# upgrade table of sign
# function upgrade_sign_sql() {
#     # check whether old=>new .sql shell in new webase-sign/script
#     sign_script_name="${PWD}/webase-sign/script/v${old_version}_v${new_version}.sql"
#     if [[ -f ${sign_script_name} ]];then
#         # get sql config of sign from common.properties
#         local ip=$(prop "sign.mysql.ip")
#         local port=$(prop "sign.mysql.port")
#         local user=$(prop "sign.mysql.user")
#         local password=$(prop "sign.mysql.password")
#         local database=$(prop "sign.mysql.database")
#         # exec .sql by mysql -e
#         mysql --user=$user --password=$password --host=$ip --port=$port --database=$database -e${sign_script_name} $--default-character-set=utf8; 
#     else
#         LOG_WARN "sign upgrade sql file of ${sign_script_name} not exist!"
#     fi
# }


# update old yml
# 根据版本号执行其中一段
# 空格需要转义
function update_node_mgr_yml() {
    mgr_yml="${PWD}/webase-node-mgr/conf/application.yml"    
    LOG_INFO "now update yml value of node-mgr in $mgr_yml"
    if [[ ! -f $mgr_yml ]]; then
        LOG_WARN "yml of node-mgr in $mgr_yml not exist!"
        exit 1
    fi
    if [[ "${new_version}x" == "v1.5.0x" ]]; then
        LOG_INFO "update yml of version ${new_version}"
        # v1.5.0 key config to check if already add
        if [[ `grep -c "appStatusCheckCycle" ${mgr_yml}` -eq '0' ]]; then
            # 将constant:开头替换为
            local old_app_config="constant:"
            local new_app_config="constant:\n\ \ deployedModifyEnable:\ true\n\ \ appRequestTimeOut:\ 300000\n\ \ appStatusCheckCycle:\ 3000\n"
            sed -i "/${old_app_config}/c${new_app_config}" ${mgr_yml}  
        fi
        if [[ `grep -c "\/api\/*" ${mgr_yml}` -eq '0' ]]; then
            # 需要空格开头
            local old_url_config="permitUrlArray:\ \/account\/login"
            local new_url_config="\ \ permitUrlArray:\ \/account\/login,\/account\/pictureCheckCode,\/login,\/user\/privateKey\/**,\/encrypt,\/version,\/front\/refresh,\/api\/*"
            sed -i "/${old_url_config}/c${new_url_config}" ${mgr_yml} 
        fi
    fi
}

## todo sed all yml's version
function update_webase_yml_version() {
    LOG_INFO "start update version of new webase..."
    for webase_name in ${zip_list[@]};
    do
        local yml_path="${PWD}/${webase_name}/conf/application.yml"
        if [[ -f $yml_path ]]; then
            # check v1.5.0 exist
            if [[ `grep -c "${new_version}" ${yml_path}` -eq '0' ]]; then
                local old_app_config="version:"
                local new_app_config="version:\ ${new_version}\n"
                sed -i "/${old_app_config}/c${new_app_config}" ${yml_path}  
            fi
        else
            echo "jump over webase-web(or h5)"
        fi
    done
}

get_version_num
main && LOG_INFO "upgrade script finished from ${old_version} to ${new_version} of ${zip_list}"
echo "end of script"
exit ${SUCCESS}
