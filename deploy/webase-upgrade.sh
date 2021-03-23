#!/bin/bash

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
force_download_zip="true"

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
    -f    [true] or [false], force download new zip and rm old zip in ${PWD}, default true
USAGE
    exit ${PARAM_ERROR}
}


while getopts C:h OPT;do
    case ${OPT} in
        o)
            old_version="$OPTARG"
            ;;
        n)
            new_version="$OPTARG"
            ;;
        f)
            force_download_zip="$OPTARG"
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


### 需要文档指明脚本做了什么操作，生产环境的运维如果分步操作怎么完成
################################################
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

# 备份node-mgr数据库，
# 从common.properties中获取两个数据库密码

# 到node-mgr中检测script/upgrade目录，有匹配v143开头的，v150的结尾的，有则执行 mysql  -e "source $sql_file"
# 到sign...同上（当前版本不增加）

# 启动新的，执行python3 deploy.py startAll
################################################


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
    # restart
    LOG_INFO "==========now webase start all=========="
    python3 deploy.py startAll  || (LOG_WARN "==========startAll failed!==========" && exit 1)
}


# function stop_all() {
#     LOG_INFO "==========now webase stop all=========="
#     python3 deploy.py stopAll  
# }

# function start_all() {
#     LOG_INFO "==========now webase start all=========="
#     python3 deploy.py startAll
# }


function pull_zip() {
    local webase_name="$1"
    local zip="${webase_name}.zip"
    if [[ "${force_download_zip}" == "true" ]];then
        # echo "now force re-download zip of webase"
        # delete old zip
        if [[ -f "$zip" ]];then
            rm -f "$zip"
        fi
    fi
    LOG_INFO "pull zip of $zip"
    curl -#LO "${cdn_url_pre}${new_version}/${zip}" 
    # webase-web.zip => webase-web-v1.5.0
    local temp_package_name="${webase_name}-${new_version}"
    unzip -o "$zip" -d "$temp_package_name"
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
# function copy_web() {
#     
# }

function copy_front() {
    LOG_INFO "copy webase-front config files"
    if [[ -d "webase-front" ]]; then
        copy "webase-front/conf/*.yml" "webase-front-${new_version}/conf/" 
        copy "webase-front/conf/*.crt" "webase-front-${new_version}/conf/" 
        copy "webase-front/conf/*.key" "webase-front-${new_version}/conf/" 
        copy "webase-front/conf/*.so" "webase-front-${new_version}/conf/" 
    else
        LOG_WARN "copy directory of webase-front not exist!"
    fi
}

function copy_node_mgr() {
    LOG_INFO "copy webase-node-mgr config files"
    if [[ -d "webase-node-mgr" ]]; then    
        copy "webase-node-mgr/conf/*.yml" "webase-node-mgr-${new_version}/conf/" 
        copy -r "webase-node-mgr/conf/log" "webase-node-mgr-${new_version}/conf/" 
    else
        LOG_WARN "copy directory of webase-node-mgr not exist!"
    fi
}

function copy_sign() {
    LOG_INFO "copy sign config files"
    if [[ -d "webase-sign" ]]; then       
        copy "webase-sign/conf/*.yml" "webase-sign-${new_version}/conf/" 
    else
        LOG_WARN "config directory of webase-sign not exist!"
    fi
}

# backup webase dir
function backup() {
    local webase_name="$1"
    # stop all
    LOG_INFO "now backup old data of ${webase_name}"
    if [[ -d "${webase_name}" ]]; then
        mv "${webase_name}" "${webase_name}-${old_version}" || (LOG_WARN "backup ${webase_name} failed!" && exit)
    else
        LOG_WARN "backup directory of ${webase_name} not exist!"
    fi    
    mv "${webase_name}-${new_version}" "${webase_name}" || (LOG_WARN "backup ${webase_name} failed!" && exit)
}


# upgrade table of node-mgr 
function upgrade_mgr_sql() {
    # check whether old=>new .sql shell in new webase-node-mgr/script
    mgr_script_name="webase-node-mgr/script/v${old_version}_v${new_version}.sql"
    if [[ -f ${mgr_script_name} ]];then
        # get sql config of mgr from common.properties
        local ip=${prop "mysql.ip"}
        local port=${prop "mysql.port"}
        local user=${prop "mysql.user"}
        local password=${prop "mysql.password"}
        local database=${prop "mysql.database"}
        local backup_mgr_dir="webase-node-mgr-${old_version}/backup_node_mgr_${old_version}.sql"
        LOG_INFO "now backup the whole database of node-mgr in $backup_mgr_dir"
        mysqldump  --user=$user --password=$password $database > $backup_mgr_dir
        # exec .sql by mysql -e
        LOG_INFO "now upgrade database of node-mgr with script $mgr_script_name"
        mysql --user=$user --password=$password --host=$ip --port=$port --database=$database -e${mgr_script_name} $--default-character-set=utf8; 
    else
        LOG_WARN "node-mgr upgrade sql file of ${mgr_script_name} not exist!"
    fi
}

# upgrade table of sign
function upgrade_sign_sql() {
    # check whether old=>new .sql shell in new webase-sign/script
    sign_script_name="webase-sign/script/v${old_version}_v${new_version}.sql"
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
        LOG_WARN "sign upgrade sql file of ${sign_script_name} not exist!"
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
    LOG_INFO "now update yml value of node-mgr in $mgr_yml"
    if [[ ! -f $mgr_yml ]]; then
        LOG_WARN "yml of node-mgr in $mgr_yml not exist!"
        exit 1
    fi
    # v1.5.0 key config to check if already add
    if [[ `grep -c "appStatusCheckCycle" ${mgr_yml}` -eq '0' ]]; then
        # 将constant:开头替换为
        local old_app_config="constant:"
        local new_app_config="constant:\n  deployedModifyEnable: true\n  appRequestTimeOut: 300000\n  appStatusCheckCycle: 3000\n"
        sed_file ${old_app_config} ${new_app_config} ${mgr_yml}  
    fi
    if [[ `grep -c "\/api\/*" ${mgr_yml}` -eq '0' ]]; then
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
    sed -i "/${old_config}/c${new_config}" ${file_path}  || (echo "sed $new_config failed!" >> "${logfile}" && exit 1)   
}

main && LOG_INFO "upgrade script finished from ${old_version} to ${new_version} of ${zip_list}"
echo "end of script"
exit ${SUCCESS}
