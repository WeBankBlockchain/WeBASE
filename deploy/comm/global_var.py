#!/usr/bin/env python3
# encoding: utf-8

default='default'
install_all='installAll'
visual_deploy='installWeBASE'

## deploy type to file mapping
_type_file_dict = {
    default: 'common.properties',
    install_all: 'common.properties',
    visual_deploy: 'visual-deploy.properties'
}

## deploy type pass in as a parameter
deploy_type = default

## set deploy type
def set_install_all():
    global deploy_type
    global install_all
    deploy_type = install_all

def set_visual_deploy():
    global deploy_type
    global visual_deploy
    deploy_type = visual_deploy


## get properties file
def get_file():
    try:
        global deploy_type
        return _type_file_dict[deploy_type]
    except KeyError:
        global default
        return _type_file_dict[default]
