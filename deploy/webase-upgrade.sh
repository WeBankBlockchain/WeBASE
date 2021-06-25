#!/bin/bash

set -e


################################################
#根据新版本到CDN下载对应版本的upgrade.sh脚本文件，并执行
################################################

####### error code
SUCCESS=0

PARAM_ERROR=5

## default one host, one node+front
old_version=
new_version=

# download url prefix
cdn_url_pre="https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/WeBASE/releases/download/"

# dependencies
depend_list=("python3" "dos2unix" "unzip" "mysql" "mysqldump" "curl")

LOG_WARN()
{
    local content=${1}
    echo -e "\033[31m[WARN] ${content}\033[0m"
    echo "[WARN] ${content}" >> ${logfile}
}

LOG_INFO()
{
    local content=${1}
    echo -e "\033[32m[INFO] ${content}\033[0m"
    echo "[INFO] ${content}" >> ${logfile}
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

function checkCurl() {
    for package in ${depend_list[@]};
    do
        if [[ ! $(command -v ${package}) ]]; then
            LOG_WARN "dependencies of [${package}] not installed, please install it and try again!"
            exit 1
        fi
    done
    LOG_INFO "check dependencies passed!"    
}

function get_upgrade() {
    if [[ ! -f "${PWD}/upgrade.sh" ]]; then
        LOG_INFO "upgrade.sh script exists, now delete and re-download"            
        rm -f ${PWD}/upgrade.sh
    fi
    curl -#LO "${cdn_url_pre}${new_version}/upgrade.sh" 
    if [[ "$(ls -al . | grep upgrade.sh | awk '{print $5}')" -lt "10000" ]];then # 1m=1048576b
        LOG_WARN "download  upgrade script failed, exit!"
        exit 1
    fi
    chmod +x upgrade.sh
    source upgrade.sh
}


## 版本号获取数字，v1.5.0 => 150
function get_version_num() {
    old_version_num=`echo "${old_version}" | tr -cd "[0-9]"`
    new_version_num=`echo "${new_version}" | tr -cd "[0-9]"`
    if [[ "${old_version_num}" -eq "" || "${old_version_num}" -eq "" ]];then
        LOG_WARN "error! please type in version"
        usage
        exit 1
    fi
    LOG_INFO "upgrade script only support nearing version (new: ${new_version_num}, old: ${old_version_num} )upgrade!"
}

get_version_num
get_upgrade
