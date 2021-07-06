#!/bin/bash

set -e

################################################
# 下载新的zip包，已存在则移动到{old_version}的目录中

# 解压新的zip包到webase-front.zip => webase-front-v1.5.0

# 停止原有的，python3 deploy.py stopAll

# webase-web 直接复制全部
# 复制已有front的conf/*.yml, *.key, *.crt, *.so，覆盖当前的文件
# 复制已有sign的conf/*.yml
# 复制已有node-mgr已有的conf的*.yml，conf/log目录
# 更新旧的yml，更新版本号

# mv操作，备份已有的，移动到{old_version}的目录中

# 备份node-mgr数据库到webase-node-mgr-v1.5.0/backup.sql
# 从common.properties中获取两个数据库密码

# 到node-mgr中检测script/upgrade目录，有匹配v143开头的，v150的结尾的，有则执行 mysql  -e "source $sql_file"
# 到sign...同上（当前版本不增加）

# 启动新的，执行python3 deploy.py startAll
################################################


## zip name
zip_list=("webase-front" "webase-web" "webase-node-mgr")

function main() {
    
    # pull 
    if [[ ! -f  "deploy.py" ]];then
        LOG_WARN "deploy.py not in this directory!"
        exit 1
    fi

    LOG_INFO "start pull zip of new webase..."

    # pull 
    if [[ ! -f  "${old_version}" ]];then
        # backup old zip
        mkdir "${old_version}"
    fi

    for webase_name in ${zip_list[@]};
    do
        echo "now [${webase_name}] pull new version zip"
        pull_zip "$webase_name"
    done

    # stop
    LOG_INFO "==========now webase stop all=========="
    python3 deploy.py stopAll 
    # todo 判断是否已停止

    # change new webase's config file, backup old webase and data
    for webase_name in ${zip_list[@]};
    do
        echo "now [${webase_name}] copy old version config & backup old files & update new data"
        copy_webase "$webase_name" 
    done

    # update version
    LOG_INFO "==========now update webase version in yml=========="
    update_webase_yml_version

    # restart
    LOG_INFO "==========now webase start all=========="
    python3 deploy.py startAll 
}


function pull_zip() {
    local webase_name="$1"
    local zip="${webase_name}.zip"
    # delete old zip
    if [[ -f "$zip" ]];then
        LOG_INFO "move old version zip $zip to directory of [$PWD/${old_version}]"
        if [[ -f "${old_version}/${zip}" ]];then
            LOG_WARN "old version zip of ${zip} already in directory ./${old_version}"
            rm -rf "${PWD}/${zip}"
        else
            mv "$zip" "${old_version}/"
        fi
    fi
    LOG_INFO "pull zip of $zip"
    curl -#LO "${cdn_url_pre}/${new_version}/${zip}" 
    if [[ "$(ls -al . | grep ${zip} | awk '{print $5}')" -lt "500000" ]];then # 1m=1048576b
        LOG_WARN "download ${zip} failed, exit!"
        exit 1
    fi
    # webase-web.zip => webase-web-v1.5.0/webase-web
    #注：unzip后变成了webase-web-v1.5.0/webase-web
    if [[ -d "${webase_name}-${new_version}" ]];then
        LOG_WARN "unzip destination dir already exist, now rm and re-unzip"
        rm -rf "${PWD}/${webase_name}-${new_version}"
    fi
    unzip -o "$zip" -d "${webase_name}-${new_version}"  > /dev/null
}

## copy config and cert to new unzip dir
# 先复制到新目录，然后再备份旧的文件夹
function copy_webase() {
    local webase_name="$1"
    case ${webase_name} in
        "webase-web")
            backup "webase-web"
            backup "webase-web-mobile"
            update_nginx_conf
            ;;
        "webase-front")
            copy_front
            backup "webase-front"   
            ##update_front_yml 
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
            ##update_sign_yml
            ##upgrade_sign_sql
            ;;            
        \?)
            LOG_WARN "not support update this service [${webase_name}]"
            ;;
    esac

}

function copy_front() {     
    LOG_INFO "copy webase-front config files"
    if [[ -d "${PWD}/webase-front" && -d "${PWD}/webase-front-${new_version}" ]]; then
        cp -f "${PWD}/webase-front/conf/application.yml" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp -f "${PWD}/webase-front/conf/log4j2.xml" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp -f "${PWD}/webase-front/conf/ca.crt" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp -f "${PWD}/webase-front/conf/sdk.crt" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp -f "${PWD}/webase-front/conf/sdk.key" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp -rf "${PWD}/webase-front/conf/gm" "${PWD}/webase-front-${new_version}/webase-front/conf/"         
        cp -f "${PWD}/webase-front/conf/libsigar-aarch64-linux.so" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp -f "${PWD}/webase-front/conf/libsigar-amd64-linux.so" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp -f "${PWD}/webase-front/conf/libsigar-universal64-macosx.dylib" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        cp -f "${PWD}/webase-front/conf/libsigar-x86-linux.so" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        if [[ -f "${PWD}/webase-front/conf/node.key" ]]; then
            cp -f "${PWD}/webase-front/conf/node.crt" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
            cp -f "${PWD}/webase-front/conf/node.key" "${PWD}/webase-front-${new_version}/webase-front/conf/" 
        fi
    else
        LOG_WARN "copy directory of ${PWD}/webase-front not exist!" 
        exit 1
    fi
}

function copy_node_mgr() {
    LOG_INFO "copy webase-node-mgr config files"
    if [[ -d "${PWD}/webase-node-mgr" && -d "${PWD}/webase-node-mgr-${new_version}" ]]; then    
        cp -f "${PWD}/webase-node-mgr/conf/application.yml" "${PWD}/webase-node-mgr-${new_version}/webase-node-mgr/conf/" 
        #cp -r "${PWD}/webase-node-mgr/conf/log" "${PWD}/webase-node-mgr-${new_version}/webase-node-mgr/conf/" 
    else
        LOG_WARN "copy directory of webase-node-mgr not exist!"
        exit 1        
    fi
}

function copy_sign() {
    LOG_INFO "copy sign config files"
    if [[ -d "${PWD}/webase-sign" &&  -d "${PWD}/webase-sign-${new_version}/webase-sign" ]]; then 
        cp -f "${PWD}/webase-sign/conf/application.yml" "${PWD}/webase-sign-${new_version}/webase-sign/conf/" 
    else
        LOG_WARN "config directory of webase-sign not exist!"
        exit 1
    fi
}



# backup webase package and use new version package
function backup() {
    local webase_name="$1"
    LOG_INFO "now backup old data of ${webase_name}"
    if [[ -d "${PWD}/${webase_name}" ]]; then
        mv "${PWD}/${webase_name}" "${PWD}/${old_version}/"
    else
        # skip v1.5.0 web-mobile upgrade, cuz added in v1.5.0
        if [[ "${new_version}" == "v1.5.0" && "${webase_name}" == "webase-web-mobile" ]]; then
            LOG_INFO "jump over webase-web-mobile backup: ${webase_name}"
        else
            LOG_WARN "backup directory of ${PWD}/${webase_name} not exist!"
            exit 1
        fi
    fi
    mv "${PWD}/${webase_name}-${new_version}/${webase_name}" "${PWD}/${webase_name}"
}


config_properties="${PWD}/common.properties"
# 定义一个函数从properties文件读取key
function prop() {
    local key="${1}"
	if [[ -f "$config_properties" ]]; then
        dos2unix $config_properties
        grep -P "^\s*[^#]?${key}=.*$" $config_properties | cut -d'=' -f2
    else 
        LOG_WARN "webase $config_properties file not found!"
        exit 1
    fi
}


# upgrade table of node-mgr after backup webase-node-mgr dir
function upgrade_mgr_sql() {
    # check whether old=>new .sql shell in new webase-node-mgr/script
    mgr_script_name="${PWD}/webase-node-mgr/script/upgrade/v${old_version_num}_v${new_version_num}.sql"
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
        exit 1
    fi
}


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
        LOG_INFO "update update_node_mgr_yml of version ${new_version}"
        # v1.5.0 key config to check if already add
        if [[ `grep -c "appStatusCheckCycle" ${mgr_yml}` -eq '0' ]]; then
            # 将constant:开头替换为
            local old_app_config="constant:"
            local new_app_config="constant:\n\ \ deployedModifyEnable:\ true\n\ \ appRequestTimeOut:\ 300000\n\ \ appStatusCheckCycle:\ 3000\n\ \ statBlockRetainMax:\ 100000\n\ \ statBlockFixedDelay: 5000\n\ \ statBlockPageSize:\ 10\n\ \ enableExternalFromBlock:\ true\n"
            sed -i "/${old_app_config}/c${new_app_config}" ${mgr_yml}  
        fi
        if [[ `grep -c "\/api\/*" ${mgr_yml}` -eq '0' ]]; then
            # 需要空格开头
            local old_url_config="permitUrlArray:\ \/account\/login"
            local new_url_config="\ \ permitUrlArray:\ \/account\/login,\/account\/pictureCheckCode,\/login,\/user\/privateKey\/**,\/config\/encrypt,\/config\/version,\/front\/refresh,\/api\/*"
            sed -i "/${old_url_config}/c${new_url_config}" ${mgr_yml} 
        fi
    fi
}

# copy webase-web and webase-web-mobile
function update_nginx_conf() {
    LOG_INFO "now update webase-web nginx file in ${PWD}/comm/nginx.conf"
    if [[ ! -f "${PWD}/comm/nginx.conf" ]]; then
        LOG_WARN "nginx config file not exist, cannot auto update, now jump over!"
        #exit 1
    fi
    local zip="webase-deploy.zip"
    curl -#LO "${cdn_url_pre}/${new_version}/${zip}" 
    if [[ "$(ls -al . | grep ${zip} | awk '{print $5}')" -lt "10000" ]];then
        LOG_WARN "update_nginx_conf pull newer webase-deploy.zip failed, exit now"
        #exit 1
    fi
    unzip -o "$zip" -d "temp-deploy"  > /dev/null
    # backup nginx conf in {old_version}
    mv "${PWD}/comm/nginx.conf" "${PWD}/${old_version}/"
    # copy new one into ./comm
    cp -f "${PWD}/temp-deploy/webase-deploy/comm/nginx.conf" "${PWD}/comm/"
    # sed new conf file
    web_port=$(prop "web.port")
    mgr_port=$(prop "mgr.port")
    local pid_file="${PWD}/nginx-webase-web.pid"
    local web_dir="${PWD}/webase-web"
    local web_log_dir="${web_dir}/log"
    local h5_web_dir="${PWD}/webase-web-mobile"
    # create log dir
    if [[ ! -d "${PWD}/${web_log_dir}" ]]; then
        mkdir -p "$web_log_dir"
    fi

    sed -i "s/5000/${web_port}/g" "${PWD}/comm/nginx.conf"
    sed -i "s/5001/${mgr_port}/g" "${PWD}/comm/nginx.conf"
    sed -i "s:log_path:${web_log_dir}:g" "${PWD}/comm/nginx.conf"
    sed -i "s:pid_file:${pid_file}:g" "${PWD}/comm/nginx.conf"
    # set web_page_url(root & static) globally
    sed -i "s:web_page_url:${web_dir}:g" "${PWD}/comm/nginx.conf"
    # set mobile phone phone_page_url globally
    sed -i "s:phone_page_url:${h5_web_dir}:g" "${PWD}/comm/nginx.conf"
    # remove temp dir    
    rm -rf "${PWD}/temp-deploy"
}


## sed all yml's version
function update_webase_yml_version() {
    LOG_INFO "start update version of new webase..."
    for webase_name in ${zip_list[@]};
    do
        local yml_path="${PWD}/${webase_name}/conf/application.yml"
        # skip v1.5.0 webase-sign upgrade
        if [[ "${new_version}" == "v1.5.1" && "${webase_name}" == "webase-sign" ]]; then
            LOG_INFO "skip upgrade to ${new_version} in webase-sign"
            continue
        fi
        if [[ -f $yml_path ]]; then
            # check new version exist
            if [[ `grep -c "${new_version}" ${yml_path}` -eq '0' ]]; then
                local old_app_config="version:"
                local new_app_config="version:\ ${new_version}\n"
                sed -i "/${old_app_config}/c${new_app_config}" ${yml_path}  
            fi
        else
            echo "jump over webase-web(or mobile)"
        fi
    done
}


exit_with_tips()
{
    local content=${1}
    echo -e "\033[31m[ERROR] ${content}\033[0m"
    echo "use webase subsystem files in ${PWD}/${old_version} to recover "
    exit 1
}

# checkDependencies
# get_version_num
main && LOG_INFO "upgrade script finished from ${old_version} to ${new_version}"
echo "end of script"
exit ${SUCCESS}
