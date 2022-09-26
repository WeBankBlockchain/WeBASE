中文|[English](README-en.md)

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://webasedoc.readthedocs.io/zh_CN/latest/docs/WeBASE/CONTRIBUTING.html)
[![license](http://img.shields.io/badge/license-Apache%20v2-blue.svg)](http://www.apache.org/licenses/)
[![GitHub (pre-)release](https://img.shields.io/github/release/WeBankBlockchain/WeBASE/all.svg)](https://github.com/WeBankBlockchain/WeBASE/releases)
[![Code Lines](https://tokei.rs/b1/github/WeBankBlockchain/WeBASE?category=code)](https://github.com/WeBankBlockchain/WeBASE)

![image](https://webasedoc.readthedocs.io/zh_CN/latest/_images/logo.jpg)

# 什么是WeBASE

**WeBASE**（WeBank Blockchain Application Software Extension） 是在区块链应用和FISCO BCOS节点之间搭建的一套通用组件，围绕交易、合约、密钥管理，数据，可视化管理来设计各个模块。开发者可以根据业务所需，选择子系统进行部署。

**WeBASE**屏蔽了区块链底层的复杂度，降低开发者的门槛，大幅提高区块链应用的开发效率，包含**节点前置**、**节点管理**、**Web管理平台**、**签名服务**、**数据导出**等子系统。

**WeBASE**将区块链应用开发标准化，搭建完FISCO BCOS节点后，只需按照五步标准流程进行区块链应用开发，开发流程请参阅 [使用WeBASE开发区块链应用](https://github.com/WeBankBlockchain/WeBASE-Doc/blob/master/docs/WeBASE/quick-start.md)

**WeBASE一键部署**(FISCO BCOS + WeBASE-Front + WeBASE-Node-Manager + WeBASE-Sign + WeBASE-Web)可以参考[WeBASE一键部署文档](https://webasedoc.readthedocs.io/zh_CN/latest/docs/WeBASE/install.html)，**WeBASE**整体结构设计与各子系统功能与安装部署的详细介绍，请参考[WeBASE在线文档](https://webasedoc.readthedocs.io/zh_CN/latest/index.html)


## 技术文档
- **WeBASE 1.x版本** 适用于FISCO-BCOS **2.x版本**，可查看 [WeBASE 1.x文档](https://webasedoc.readthedocs.io/zh_CN/latest/index.html) (stable)
- **WeBASE 3.x版本** 适用于FISCO-BCOS **3.x版本**，可查看 [WeBASE 3.x文档](https://webasedoc.readthedocs.io/zh_CN/lab)，相关代码位于master-3.0分支

## 各子系统简介
* **节点前置服务 [WeBASE-Front](https://github.com/WeBankBlockchain/WeBASE-Front)** 
集成java-sdk，提供restful风格的接口，客户端可以使用http的形式和节点进行交互，内置内存数据库，采集节点健康度数据。内置web控制台，实现节点的可视化、合约部署IDE等功能。

* **节点管理服务 [WeBASE-Node-Manager](https://github.com/WeBankBlockchain/WeBASE-Node-Manager)**
处理WeBASE-Web前端页面所有web请求，基于前置服务，管理各个节点的状态，管理链上所有智能合约，对区块链的数据进行统计、分析，对异常交易的审计，私钥管理等。

* **WeBASE管理平台 [WeBASE-Web](https://github.com/WeBankBlockchain/WeBASE-Web)**
基于节点管理服务的可视化操作平台，可基于此平台查看节点信息，开发智能合约等。

* **交易服务 [WeBASE-Transcation](https://github.com/WeBankBlockchain/WeBASE-Transcation)**
接收交易请求，缓存交易到数据库中，异步上链，可大幅提升吞吐量，解决区块链的tps瓶颈问题。

* **私钥托管和签名服务 [WeBASE-Sign](https://github.com/WeBankBlockchain/WeBASE-Sign)**
托管用户私钥，提供云端签名。

* **数据导出代码生成工具 [WeBASE-Codegen-Monkey](https://github.com/WeBankBlockchain/WeBASE-Codegen-Monkey)**
代码生成工具，通过配置可以生成数据导出的核心代码。

* **数据导出服务 [WeBASE-Collect-Bee](https://github.com/WeBankBlockchain/WeBASE-Collect-Bee)**
导出区块链上的基础数据，如当前块高、交易总量等，通过智能合约的配置，导出区块链上合约的业务数据，包括event、构造函数、合约地址、执行函数的信息等。

* **链管理服务 [WeBASE-Chain-Manager](https://github.com/WeBankBlockchain/WeBASE-Chain-Manager)** 
链管理服务支持管理多条链，支持国密链、非国密链。对外提供群组的增删查改接口，让用户可以便捷地建立自己应用的群组。

* **合约安全检测服务 [WeBASE-Solidity-Security](https://github.com/WeBankBlockchain/WeBASE-Solidity-Security)** 
合约安全检测服务继承了solidity合约检测工具slither，对外提供检测接口。

* **数据统计服务 [WeBASE-Stat](https://github.com/WeBankBlockchain/WeBASE-Stat)** 
统计数据服务以前置为基础，拉取CPU、内存、IO、群组大小、群组gas、群组网络流量的数据，记录数据库。

* **数据监管服务 [WeBASE-Data](https://github.com/WeBankBlockchain/WeBASE-Data)** 
数据监管服务以前置为基础，导出区块链数据并解析，提供一个可视化的监管视图。可以查询交易属于哪条链，哪个用户，哪个合约，保证链上数据可查可管。


## 贡献说明
请阅读我们的[贡献文档](https://webasedoc.readthedocs.io/zh_CN/latest/docs/WeBASE/CONTRIBUTING.html)，了解如何贡献代码，并提交你的贡献。

希望在您的参与下，WeBASE会越来越好！

## 社区
联系我们：webase@webank.com

社区小助手微信ID : WeBank_Blockchain
